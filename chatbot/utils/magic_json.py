from typing import Any, Hashable


class Json(dict):
    '''Javascript-style json. You can access values in dict as dict's attributes.
    Examples:
        You can access keys like instance's properties::
            new_json = JsonDict(key='value')
            new_json.key
            >>> 'value'
        You can set keys as properties::
            new_json.key = 'something new'
            new_json
            >>> {'key': 'something new'}
        Finally, it's allowed to delete attributes to remove appropriate keys::
            del new_json.key
            new_json
            >>> {}
    '''

    def __init__(self, *args: Any, **kwargs: Any):
        '''
        Transforms sub-dictionaries to Json objects recursively.
        '''

        args = [Json(**arg) if isinstance(arg, dict) else arg for arg in args]

        for key, value in kwargs.items():
            if isinstance(value, dict):
                kwargs[key] = Json(value)

        super().__init__(*args, **kwargs)

    def __repr__(self) -> str:

        return f'Json {dict(self)!r}'

    def __getattr__(self, key: Hashable) -> Any:
        try:
            return self[key]
        except KeyError as err:
            raise AttributeError(key) from err

    def __setattr__(self, key: Hashable, value: Any) -> None:
        self[key] = value

    def __delattr__(self, key: Hashable) -> None:

        if key in self:
            del self[key]
        else:
            super().__delattr__(str(key))
