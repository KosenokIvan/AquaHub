class UserNotFoundError(Exception):
    pass


class NicknameAlreadyUseError(Exception):
    pass


class EmailAlreadyUseError(Exception):
    pass


class IncorrectNicknameOrPasswordError(Exception):
    pass


class ArticleNotFoundError(Exception):
    pass


class ForbiddenToUserError(Exception):
    pass


class CommentNotFoundError(Exception):
    pass
