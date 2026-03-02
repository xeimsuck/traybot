from aiogram.fsm.state import StatesGroup, State

class RenameDevice(StatesGroup):
    waiting_for_name = State()