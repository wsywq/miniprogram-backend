from fastapi import HTTPException, status


class HabitTrackerException(Exception):
    """Base exception for habit tracker"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class UserNotFoundException(HabitTrackerException):
    def __init__(self, message: str = "User not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class HabitNotFoundException(HabitTrackerException):
    def __init__(self, message: str = "Habit not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class CheckinAlreadyExistsException(HabitTrackerException):
    def __init__(self, message: str = "Check-in already exists for this date"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class InsufficientPointsException(HabitTrackerException):
    def __init__(self, message: str = "Insufficient points"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class InvalidWeChatCodeException(HabitTrackerException):
    def __init__(self, message: str = "Invalid WeChat code"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class UnauthorizedException(HabitTrackerException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)
