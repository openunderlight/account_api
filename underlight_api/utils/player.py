# Constants
ACCT_ADMIN = 'A'
ACCT_KILLED = 'K'
ACCT_LOCKED = 'L'
ACCT_MONSTER = 'M'
ACCT_PLAYER = 'P'
ACCT_PMARE = 'S'
ACCT_ADMIN_EXPIRED = 'E'
ACCT_PLAYER_EXPIRED = 'X'

# Type to text
STATUS_DESCRIPTIONS = {
    ord(ACCT_ADMIN[0]): 'admin',
    ord(ACCT_KILLED[0]): 'killed',
    ord(ACCT_LOCKED[0]): 'locked',
    ord(ACCT_MONSTER[0]): 'agent',
    ord(ACCT_PLAYER[0]): 'player',
    ord(ACCT_PMARE[0]): 'pmare',
    ord(ACCT_ADMIN_EXPIRED[0]): 'expired_admin',
    ord(ACCT_PLAYER_EXPIRED[0]): 'expired_player',
}