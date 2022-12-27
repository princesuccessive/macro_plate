from celery import current_task


def update_task_progress(total, current, **kwargs):
    """Update current task progress."""
    if not current_task:
        return

    meta = dict(total=total, done=current)
    meta.update(**kwargs)

    current_task.update_state(
        state='PROGRESS',
        meta=meta,
    )
