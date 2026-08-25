class BookingError(Exception):
    """Base class for all booking-related validation errors."""

    status_code = 400

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class DoctorNotAvailableError(BookingError):
    """Raised when a doctor has no working hours on the given date,
    or the requested slot falls outside them."""

    status_code = 400


class SlotInPastError(BookingError):
    status_code = 400


class SlotWithinBufferError(BookingError):
    """Raised when the slot starts within the 1-hour booking buffer."""

    status_code = 400


class SlotAlreadyBookedError(BookingError):
    status_code = 409  # Conflict


class AppointmentNotFoundError(BookingError):
    status_code = 404


class AppointmentAlreadyCancelledError(BookingError):
    status_code = 400


class AppointmentInPastError(BookingError):
    """Raised when trying to cancel or reschedule an appointment
    whose original time has already passed."""

    status_code = 400

class InvalidSlotAlignmentError(BookingError):
    """Raised when a requested time doesn't align to a valid 30-minute slot boundary."""

    status_code = 400