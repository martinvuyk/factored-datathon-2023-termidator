from typing import Callable, Optional, TypeVar
from typing_extensions import TypeGuard

T = TypeVar("T")


def try_false_type_guard(
    fn: Callable[..., TypeGuard[T]]
) -> Callable[..., TypeGuard[T]]:
    """a wrapper so that the function only handles the positive case for the TypeGuard.\n
    if the function is void or an error occurs, returns False"""

    def new_fn(*args, **kwargs) -> bool:
        try:
            ret: Optional[bool] = fn(*args, **kwargs)
            if ret is None:
                return False
            return ret
        except:
            return False

    # Get back the docstrings
    new_fn.__doc__ = fn.__doc__
    return new_fn
