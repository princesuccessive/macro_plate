from .model_admin import ForbidDeleteAdd


class NonEditableInline(ForbidDeleteAdd):
    """Inline with not not editable fields."""
    extra = 0
    max_num = 0
