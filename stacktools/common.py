import os
from pwd import getpwnam

def demote(user_uid, user_gid):
    """Pass the function 'set_ids' to preexec_fn, rather than just calling
    setuid and setgid. This will change the ids for that subprocess only"""

    def set_ids():
        os.setgid(user_gid)
        os.setuid(user_uid)

    return set_ids


def get_stack_user_info():
	user_info = getpwnam('stack')
	return (user_info.pw_uid, user_info.pw_gid)
