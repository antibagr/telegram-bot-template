import logging
import os
import asyncio
from datetime import datetime, timedelta
import random
from functools import wraps
from typing import Union, Optional, List

from telethon import TelegramClient
from telethon import functions, types
from telethon.tl.types import PeerUser, PeerChannel, PeerChat, User
from telethon.tl.functions.channels import InviteToChannelRequest, \
    CreateChannelRequest
from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.errors import rpcerrorlist, FloodWaitError


from config import TG_API_ID, TG_API_HASH, BOT_USERNAME, APP_NAME, TELETHON_PHONE, ADMIN_ID, BASE_DIR, MAGIC_ID
from exceptions import (
    EmptyCodeException, InvalidCodeException, ResendCodeLimit,
    BaseTelethonException, VerboseTelethonException,  NotInMutualContactsException)



from manager.models import OrderModel

from utils.async_func import async_task
from handlers.errors.send_exception import send_exception
from interface.verbose import msg


logging.getLogger('telethon').setLevel(logging.INFO)


def ConnectToClient(func):

    @wraps(func)
    async def ClientGetter(*args, **kw):
        caller = func.__name__
        logging.info(f'Getting a client for a {caller}')
        client = await asyncio.wait_for(ConnectionMaster.GetClient(caller), timeout=999999999)
        logging.info(f'Got a client for a {caller}')

        try:
            results = await func(client, *args, **kw)
        except FloodWaitError as e:
            await send_exception(
                e,
                {
                    "FloodWaitError":
                    f'{caller} has a flood wait set to {e.seconds} seconds '
                }
            )

            logging.exception(e, exc_info=True)
            asyncio.create_task(ConnectionMaster.SetFloodWaiter(e.seconds))
            # recursive call with updated flood time value
            return await ClientGetter(*args, **kw)

        return results
    return ClientGetter


class ConnectionMaster():

    # const
    WAITCLOCK = 60 # sec
    CONNECTION_RETRY_DELAY = 60 # sec
    RESEND_CODE_LIMIT = 5
    RESEND_CODE_DELAY = 300 # minutes
    READ_CODE_DELAY = 60 # seconds

    client = None
    connected = False
    PathToCode = os.path.join(BASE_DIR, "src", "chatbot", "code.txt")
    is_waiting_code = False
    Code = None
    FloodWait = 0
    attempts = 0

    @classmethod
    def ReadCode(cls) -> str:
        try:
            with open(cls.PathToCode, 'r') as f:
                Code = f.read()
                if Code == '':
                    raise EmptyCodeException()
                elif len(Code) < 5 or not Code.isdigit():
                    raise InvalidCodeException(Code)
                else:
                    logging.warning(f"Code was found: {Code}")
                    return Code

        except FileNotFoundError:
            logging.info(f"File {cls.PathToCode} is not presented")
        except EmptyCodeException as e:
            logging.info(e)
        except InvalidCodeException as e:
            logging.exception(e)
            logging.info("Invalid code was erased")
            async_task(send_exception(e))
            open(cls.PathToCode, 'w').close()
        except Exception as e:
            logging.exception(e, exc_info=True)

    @classmethod
    async def SomebodyWaitsCode(cls, caller: str) -> TelegramClient:
        while cls.is_waiting_code:
            logging.info(f"{caller} is waiting for code")
            await asyncio.sleep(cls.READ_CODE_DELAY)
        return cls.client

    @classmethod
    async def SetFloodWaiter(cls, seconds: int):

        assert isinstance(seconds, int)

        if cls.FloodWait != 0:
            return logging.warning("Flood time is already counting!")

        logging.info(f"Flood waiting set of {seconds}")
        cls.FloodWait = seconds
        while cls.FloodWait > 0:
            cls.FloodWait -= cls.WAITCLOCK
            logging.info(f"Flood waiting set of {cls.FloodWait}")
            await asyncio.sleep(cls.WAITCLOCK)
        cls.FloodWait = 0

    @classmethod
    async def GetClient(cls, caller: str = "unknown") -> TelegramClient:

        if cls.FloodWait > 0:
            logging.warning(
                f"Flood wait received. Wait {cls.FloodWait} before getting a client for a {caller}")
            while cls.FloodWait > 0:
                await asyncio.sleep(cls.WAITCLOCK)
            logging.info("Waiting complete. Set FloodWait to zero.")

        logging.info(f"Start to getting a client for a {caller}")
        if not cls.client:
            cls.client = TelegramClient(APP_NAME, TG_API_ID, TG_API_HASH)

            connection_attempt = 0
            while not cls.connected:
                connection_attempt += 1
                try:
                    logging.info(f"Trying to connect to Telegram server ({connection_attempt})")
                    await ConnectionMaster.client.connect()
                    cls.connected = cls.client.is_connected()
                except Exception as e:
                    logging.error(e, exc_info=True)
                    await asyncio.sleep(cls.CONNECTION_RETRY_DELAY)
        if not await cls.client.is_user_authorized():

            if cls.is_waiting_code:
                return await cls.SomebodyWaitsCode(caller)

            await cls.ReceiveCode(caller)

        logging.info(f"Telegram is authorized for a {caller}")
        return cls.client

    @classmethod
    async def ReceiveCode(cls, caller: str = "unknown") -> None:

        from handlers.admin.telegram_code import SendCodeRequest, SendCodeFailedMessage

        logging.info(f"User is not authorized. Start authorizing for a {caller}")
        cls.is_waiting_code = True
        cls.Code = None
        open(cls.PathToCode, 'w').close()

        for attempt in range(1, cls.RESEND_CODE_LIMIT+1):
            logging.info(f"Attempt {attempt}")
            cls.attempts += attempt
            if cls.attempts >= cls.RESEND_CODE_LIMIT:
                cls.is_waiting_code = False
                raise ResendCodeLimit(f"Raised by a {caller}")
            cls.SentCode = await cls.client.send_code_request(TELETHON_PHONE)
            logging.info(f"New code was sent for a {caller}")
            SendingTime = datetime.now()
            asyncio.create_task(SendCodeRequest(
                SendingTime + timedelta(minutes=cls.RESEND_CODE_DELAY)))
            while ((datetime.now() - SendingTime).total_seconds() / 60.0) < cls.RESEND_CODE_DELAY:
                logging.info(
                    f"Trying to get code from a file {(datetime.now() - SendingTime).total_seconds() / 60.0}")
                # wait one minute before next attempt to get the code

                Code = cls.ReadCode()
                if Code:
                    break
                else:
                    logging.info(
                        f"Sleeping {cls.READ_CODE_DELAY} seconds before next attempt")
                    await asyncio.sleep(cls.READ_CODE_DELAY)
            if Code:
                break
        logging.warning(f"Code was received for a {caller}! {Code}")
        cls.is_waiting_code = False

        try:
            await cls.client.sign_in(TELETHON_PHONE, code=Code, phone_code_hash=cls.SentCode.phone_code_hash)
        except rpcerrorlist.PhoneCodeExpiredError as e:
            logging.exception(e, exc_info=True)
            open(cls.PathToCode, 'w').close()

            await SendCodeFailedMessage(msg.admin.code_expired)

            # recursive call
            cls.client = await cls.GetClient(caller)
        except rpcerrorlist.PhoneCodeInvalidError as e:
            logging.exception(e, exc_info=True)
            open(cls.PathToCode, 'w').close()

            await SendCodeFailedMessage(msg.admin.invalid_code)

            # recursive call
            cls.client = await cls.GetClient(caller)
        except Exception as e:
            logging.exception(e, exc_info=True)
            open(cls.PathToCode, 'w').close()

            await send_exception(e)
            cls.client = await cls.GetClient(caller)

        else:
            logging.info(f"Ta-da. Successfully signed in for a {caller}")


class TelethonClass:

    def __init__(self) -> None:
        logging.debug("TelethonClass created")


    @staticmethod
    async def sleep_delay(min: Optional[int] = 1, max: Optional[int] = 3) -> None:
        await asyncio.sleep(random.randint(min, max))

    @staticmethod
    def get_chat_id(chat_id: Union[int, str]) -> int:
        return int("-100" + str(chat_id))

    @ConnectToClient
    async def create_private_chat(client, order: OrderModel) -> int:
        """Create new telegram chat and return its id

        Parameters
        ----------

        order : OrderModel
            OrderModel to create chat to

        """

        logging.debug(f"Creating new telegram chat for order {order}")

        # Create new chat

        new_chat = await client(CreateChannelRequest(
                title=f"Заказ {order}",
                about=order.get_description(),
                megagroup=True
        ))

        await TelethonClass.sleep_delay(5, 10)

        # We add bot to the new chat

        await client(InviteToChannelRequest(
            new_chat.chats[0],
            [await client.get_entity(BOT_USERNAME)]
        ))

        await TelethonClass.sleep_delay(5, 10)

        # Edit permissions and set bot as an administrator

        await client([functions.channels.EditAdminRequest(
            channel=new_chat.chats[0],
            user_id=BOT_USERNAME,
            admin_rights=types.ChatAdminRights(
                change_info=True,
                post_messages=True,
                edit_messages=True,
                delete_messages=True,
                ban_users=True,
                invite_users=True,
                pin_messages=True,
                add_admins=True
                ),
            rank="Арбитр заказа"),
            ])

        await client(functions.account.UpdateNotifySettingsRequest(
            peer=new_chat.chats[0].id,
            settings=types.InputPeerNotifySettings(
                silent=True,
                mute_until=datetime(2025, 1, 1),
            )
        ))

        return TelethonClass.get_chat_id(new_chat.chats[0].id)


    @ConnectToClient
    async def get_all_members(client, chat_id: int) -> List[User]:

        all_participants = client.iter_participants(chat_id)

        participants: List[User] = []

        async for participant in all_participants:

            if participant.username != BOT_USERNAME and not participant.is_self:
                participants.append(participant)

        return participants


    @ConnectToClient
    async def delete_all_messages(client, chat_id: int):

        ids = []
        async for message in client.iter_messages(chat_id):
          await client.delete_messages(chat_id, message.id)


    @ConnectToClient
    async def EditAdmin(client, chat, admin, _=None, **kwargs):
        await client.edit_admin(chat, admin, **kwargs)

    @ConnectToClient
    async def say_hello(client):
        await client.send_message('me', 'Hello, myself!')

    @ConnectToClient
    async def GetChatInviteLink(client, ChatId) -> Union[str, None]:
        """ Returns link if has one or None due to exception """

        try:
            Chat = await TelethonClass.GetChatEntity(ChatId)
        except ValueError:
            Chat = None

        try:
            if Chat:
                # return: ChatInviteExported(link='https://t.me/joinchat/<link>')
                ChatEntity = await client(ExportChatInviteRequest(Chat))
                return ChatEntity.link
        except rpcerrorlist.ChatAdminRequiredError as e:
            raise VerboseTelethonException(TelethonClass.GetChatInviteLink, alert=str(
                e), verbose=msg.err.not_an_admin_in_the_chat)
        except rpcerrorlist.PeerIdInvalidError:
            logging.error("Accont has no access to the chat", exc_info=True)
        except Exception as e:
            logging.exception(e, exc_info=True)
            await send_exception(e)

        # Return None if an error happened
        return None

    @ConnectToClient
    async def delete_PrivateChat(client, chat_id: int) -> bool:
        try:
            logging.info(f"Start deleting chat {chat_id}...")
            result = await client(functions.channels.DeleteChannelRequest(
                channel=chat_id
                ))
            logging.info(result.stringify())
            return True
        except rpcerrorlist.ChannelPrivateError as e:
            async_task(send_exception(e, "ChannelPrivateError in delete_PrivateChat"))
        except Exception as e:
            async_task(send_exception(e, "Exception in delete_PrivateChat"))

        return False

    @ConnectToClient
    async def send_message(client, receiver_id: int, text: str, contact: bool = False):
        if contact:
            receiver = receiver_id  # User's phone passed
        else:
            receiver = await client.get_entity(PeerUser(receiver_id))
        await client.send_message(receiver, text)

    # async def AddContact(client: TelegramClient, Contact: Union[models.UserModel, models.MentorModel]):
    #
    #     if Contact.phone_number is None:
    #         raise VerboseTelethonException(TelethonClass.AddContact, verbose=msg.err.mentor_has_no_phone.format(name=Contact.get_name()))
    #     if Contact.first_name is None:
    #         raise VerboseTelethonException(TelethonClass.AddContact, verbose=msg.err.mentor_has_no_first_name.format(name=Contact.get_name()))
    #
    #     try:
    #         logging.info(f"Trying to add new contact : {Contact.full_name}")
    #         await client(functions.contacts.ImportContactsRequest(
    #             contacts=[types.InputPhoneContact(
    #                 client_id=random.randrange(-2**63, 2**63),
    #                 phone=str(Contact.phone_number),
    #                 first_name=Contact.first_name,
    #                 last_name=Contact.last_name
    #                 )]
    #             ))
    #
    #         NewContact = await client(functions.contacts.AddContactRequest(
    #             id=Contact.id,
    #             first_name=Contact.first_name,
    #             last_name=Contact.last_name,
    #             phone=str(Contact.phone_number)
    #             ))
    #     except Exception as e:
    #         logging.exception(e, exc_info=True)
    #         asyncio.create_task(send_exception({}, e))
    #         return False
    #     else:
    #         return NewContact

    @ConnectToClient
    async def GetChatEntity(client, chat_id, _=None) -> Union[PeerChat, None]:
        try:
            chat_id = int(chat_id)
        except (ValueError, TypeError):
            logging.info(f"{chat_id} is not a valid chat identificator")
            raise BaseTelethonException(
                TelethonClass.GetChatEntity, f"Sorry cannot find chat {chat_id}")
        try:
            Entity = await client.get_entity(PeerChannel(chat_id))
        except rpcerrorlist.PeerIdInvalidError:
            Entity = await client.get_entity(PeerChat(chat_id))
        except Exception as e:
            logging.exception(e, exc_info=True)
        else:
            return Entity

        return None

    # @ConnectToClient
    # async def AddMentorToChat(client, chat_id: int, Mentor: models.MentorModel) -> bool:
    #     """
    #     AddMentorToChat. Invite mentor to the chat and add his contact if neccessary
    #     :param chat_id: id of the chat
    #     :param Mentor: MentorModel from Postgres
    #     :return: bool
    #     """
    #
    #     Contact = await TelethonClass.AddContact(client, Mentor)
    #     if not Contact:
    #         raise BaseTelethonException(
    #             TelethonClass.AddMentorToChat, f"Sorry cannot add new contact of {Mentor.full_name}")
    #
    #     ChatEntity = await TelethonClass.GetChatEntity(chat_id)
    #     if not ChatEntity:
    #         raise VerboseTelethonException(TelethonClass.AddMentorToChat, verbose=msg.err.no_such_chat.format(action="добавлении наставника"))
    #     try:
    #         await client(InviteToChannelRequest(ChatEntity, [Contact.users[0]]))
    #     except rpcerrorlist.UserNotMutualContactError as e:
    #         logging.exception(e, exc_info=True)
    #         raise NotInMutualContactsException(
    #             TelethonClass.AddMentorToChat, verbose=msg.err.mentor_not_in_mutual)

    @ConnectToClient
    async def kick_member(client, chat_id: int, member_id: int, raise_exc: Optional[bool] = False) -> None:
        try:
            await client.kick_participant(chat_id, member_id)
        except Exception as e:
            if raise_exc:
                raise
            logging.exception(e, exc_info=True)

    @ConnectToClient
    async def RemoveMentorFromChat(client, ChatId: int, MentorId: int):
        try:
            result = await client.kick_participant(int(ChatId), int(MentorId))
        except ValueError as e:
            logging.exception(e, exc_info=True)
            raise VerboseTelethonException(TelethonClass.RemoveMentorFromChat, verbose=msg.err.no_such_chat.format(action="удалении наставника"))
        except rpcerrorlist.ChatAdminRequiredError as e:
            logging.exception(e, exc_info=True)
            raise VerboseTelethonException(TelethonClass.RemoveMentorFromChat, verbose=msg.err.helper_is_not_admin)
        except rpcerrorlist.UserNotParticipantError as e:
            logging.warning(f"Mentor {MentorId} is not a participant of a chat {ChatId}")

    @ConnectToClient
    async def GetEntity(client, EntityLike):
        try:
            return await client.get_entity(EntityLike)
        except ValueError:
            print(f"Couln't get entity for {EntityLike}")
            return None

    @ConnectToClient
    async def GetEntityWithTitle(client, title):
        my_private_channel = None
        async for dialog in client.iter_dialogs():
            if dialog.name == title:
                my_private_channel = dialog
                break

        if my_private_channel is None:
            print(" "*50, f"chat {title} not found")
        else:
            print(f"chat {title} found")
        return my_private_channel
