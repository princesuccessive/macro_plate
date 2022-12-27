function addAsyncAction({
                          buttonId,
                          celeryUrl,
                          requestData,
                          csrftoken,
                          onSuccess,
                          onError,
                          withFile,
                        }) {
  if (!celeryUrl) {
    console.error('Url not specified');
    return;
  }

  const button = $(`#${buttonId}`);

  button.append(
    "<span" +
    " id='" + buttonId + "-spinner'" +
    " class='spinner-border spinner-border-sm'" +
    " role='status'" +
    " style='display: none'" +
    " aria-hidden='true'></span> ");
  button.append("<span id='" + buttonId + "-progress' style='display: none'></span>");

  const spinner = $(`#${buttonId}-spinner`);
  const progress = $(`#${buttonId}-progress`);

  /** Handlers for RUN method. */
  const runHandlers = {
    /*** Handler for success task run */
    success(data) {
      loadingStart();
      getProgress(data.task_id);
    },

    /*** Handler for failure task run */
    error(data) {
      onError(data);
    },
  };

  /** Run celery task for Assignment meals */
  function runTask() {
    const data = requestData();

    $.ajaxSetup({
      beforeSend: function (xhr) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    });
    loadingStart();

    if (withFile) {
      $.ajax({
        type: 'POST',
        url: celeryUrl,
        data: data,
        contentType: false, // NEEDED, DON'T OMIT THIS (requires jQuery 1.6+)
        processData: false, // NEEDED, DON'T OMIT THIS
        success: runHandlers.success,
        error: runHandlers.error,
      });
    } else {
      $.ajax({
        type: 'POST',
        contentType: "application/json",
        url: celeryUrl,
        dataType: "json",
        data: JSON.stringify(data),
        success: runHandlers.success,
        error: runHandlers.error,
      });
    }
  }

  function loadingStart() {
    button.attr('disabled', 'disabled');
    spinner.show();
    progress.text('0%');
    progress.show();
  }

  function loadingEnd() {
    button.removeAttr('disabled');
    spinner.hide();
    progress.hide();
  }

  /** Handlers for PROGRESS method. */
  const progressHandlers = {
    /** Handler progress data */
    success(data) {
      const state = data.state;
      const info = data.info || {};
      const taskId = data.id;

      // handle task finish
      if (state === 'SUCCESS') {
        onSuccess(info);
        loadingEnd();
        return;
      }

      // handle task fail
      if (state === 'FAILURE') {
        onError(info);
        loadingEnd();
        return;
      }

      // handle task progress
      if (state === 'PENDING' || state === 'STARTED' || state === 'PROGRESS') {
        const total = info.total || 1;
        const done = info.done || 0;

        progress.text(Math.floor(done / total * 100) + "%");
        setTimeout(() => getProgress(taskId), 3000);
      }
    },

    /** Handler error progress */
    error(data) {
      onError(data);
      loadingEnd();
    },
  };

  /** Get progress of the task */
  function getProgress(taskId) {
    $.ajax({
      type: 'GET',
      url: celeryUrl + taskId + '/',
      dataType: "json",
      success: progressHandlers.success,
      error: progressHandlers.error,
    });
  }

  button.click(runTask);
}

/**
 * Open link in new tab
 * @param url
 */
function openInNewTab(url) {
  const win = window.open(url, '_blank');
  if (win) {
    win.focus();
  }
}

/**
 * Show alert
 *
 * @param alert - alert element
 * @param message
 * @param type - bootstrap type
 */
function showAlert(alert, message, type) {
  alert.html(
    `<div class="text">${message}</div>\n` +
    '<button type="button" class="close" data-dismiss="alert" aria-label="Close">\n' +
    '  <span aria-hidden="true">&times;</span>\n' +
    '</button>'
  );
  alert.removeAttr('class');
  alert.attr('class', `alert alert-${type}`);
  alert.show();
}
