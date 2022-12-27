/** Get only local date from Date object */
function getDate(dateTime) {
  return dateTime.getFullYear() + '-' + (dateTime.getMonth() + 1) + '-' + dateTime.getDate();
}

/**
 * Send GET request to the url with some data and return the promise
 * @param url
 * @param data - object with query params
 */
function requestGET(url, data) {
  return new Promise((resolve, reject) => {
    $.ajax({
      type: 'GET',
      contentType: "application/json",
      url,
      data,
      success: resolve,
      error: reject,
    });
  });
}


/**
 * Send PUT request to the url with some data and return the promise
 * @param url
 * @param data - object with query params
 * @param csrftoken - token for request
 */
function requestPUT(url, data, csrftoken) {
  return new Promise((resolve, reject) => {
    $.ajaxSetup({
      beforeSend: function (xhr) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    });

    $.ajax({
      type: 'PUT',
      contentType: "application/json",
      url,
      dataType: "json",
      data: JSON.stringify(data),
      success: resolve,
      error: reject,
    });
  });
}


/** Default meals order in the calendar */
const mealsOrder = ['breakfast', 'lunch'];


/**
 * Function to initialize calendar on for the customer schedule.
 *
 * @param csrftoken - token for PUT and POST requests
 * @param apiUrlAssigned - API url for fetching assigned meals
 * @param apiUrlScheduled - API url for fetching scheduled meals
 * @param urlListOfMeals - UI url for meals list
 * @param customerId - current customer ID
 * @param defaultWeeklySchedule - schedule for current customer
 * @param firstDeliveryDate - first delivery date for user
 * @param calendarElementId - element id for calendar
 * @param draggableContainerElementId - element id for draggable container
 * @param draggableItemSelector - selector for draggable items in container
 * @param trashElementId - element id fot trash
 * @param spinnerElementId - element id for spinner (overall)
 */
function initializeCustomerCalendar({
                                      csrftoken,
                                      apiUrlAssigned,
                                      apiUrlScheduled,
                                      urlListOfMeals,
                                      customerId,
                                      defaultWeeklySchedule,
                                      firstDeliveryDate,
                                      calendarElementId,
                                      draggableContainerElementId,
                                      draggableItemSelector,
                                      trashElementId,
                                      spinnerElementId,
                                    }) {
  firstDeliveryDate = new Date(firstDeliveryDate);

  /** Element for Full Calendar */
  const calendarEl = document.getElementById(calendarElementId);

  /** Element for Full Calendar Draggable items */
  const draggableContainerEl = document.getElementById(draggableContainerElementId);

  /** Element for Full Calendar Trash */
  const trash = $(`#${trashElementId}`);

  /** Spinner element */
  const spinner = $(`#${spinnerElementId}`);


  /**
   * Loaded date range. This is needed for updating
   * When date is cleared we need to know that this day was.
   */
  const changedDateRange = {
    start: null,
    end: null,
  };

  /** Update start and end changed dates */
  function updateChangedDateRange(newDate) {
    if (!changedDateRange.start || (changedDateRange.start > newDate)) {
      changedDateRange.start = newDate;
    }
    if (!changedDateRange.end || (changedDateRange.end < newDate)) {
      changedDateRange.end = newDate;
    }
  }

  /** Start date of today */
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  /** Already assigned dates */
  const assignedDates = new Set();

  let spinnerCount = 0;

  function addFirstDeliveryDateBackgroundEvent() {
    calendar.addEvent({
      start: '2000-01-01',
      end: getDate(firstDeliveryDate),
      rendering: 'background',
      backgroundColor: '#ffb0b0',
    })
  }

  /** Show spinner and increase spinner count */
  function loadingStart() {
    spinnerCount++;
    spinner.show();
  }

  /** Decrease spinner count and hide spinner, if count equal to 0 */
  function loadingEnd() {
    spinnerCount = Math.max(spinnerCount - 1, 0);
    if (spinnerCount === 0) {
      spinner.hide();
    }
  }

  /** Fetch list of all assigned meals and map them to FC not editable events */
  function getAssignedEvents(info, fcSuccessCallback, fcFailureCallback) {
    const requestData = {
      customer_id: customerId,
      start: getDate(info.start),
      end: getDate(info.end),
      today: getDate(today),
    };

    loadingStart();
    requestGET(apiUrlAssigned, requestData)
      .then(items => {
        const events = items.map(item => ({
          id: item.id,
          title: item.meal_name,
          url: urlListOfMeals + item.meal_id,
          date: item.date,
          editable: false,
          classNames: 'assigned-meal',
        }));

        /* remember assigned dates to deny changing this days */
        events.forEach(event => assignedDates.add(event.date));

        fcSuccessCallback(events);
      })
      .catch(fcFailureCallback)
      .finally(() => loadingEnd());
  }

  /** Fetch list of all scheduled meals and map them to FC editable events */
  function getScheduledEvents(info, fcSuccessCallback, fcFailureCallback) {
    const requestData = {
      customer_id: customerId,
      start: getDate(info.start),
      end: getDate(info.end),
      today: getDate(today),
    };

    loadingStart();
    requestGET(apiUrlScheduled, requestData)
      .then(items => {
        const events = items.map(item => ({
          id: item.id,
          title: item.type,
          date: item.date,
          classNames: `scheduled-meal ${item.type} ${item.custom ? 'custom' : ''}`,
          custom: item.custom,
          type: item.type,
        }));

        /*
         This is the hack for the scheduled meals.
         The problem is that when adding events via `fcSuccessCallback`,
         the calendar deletes them when changing the page. And all the changes
         made are lost.
         If we add an event manually without specifying the second parameter of
         the source ID, it is not deleted when changing the page. However, you
         must be careful to avoid duplicates.
         */
        events.forEach(event => {
          if (!calendar.getEventById(event.id)) {
            calendar.addEvent(event);
          }
        });

        fcSuccessCallback([]);
      })
      .catch(fcFailureCallback)
      .finally(() => loadingEnd());
  }

  /**
   * Sent all loaded events to backend
   * To save events, we first convert them to DTO, which is waiting for the API,
   * and then send them, as well as an additional date range for which these
   * elements are used. This is necessary to track the days when all events
   * were deleted.
   */
  function saveChanges() {
    const events = calendar.getEvents();

    const dtos = events.map(event => ({
      date: getDate(event.start),
      type: event.extendedProps.type,
    })).filter(dto => dto.type);


    const requestData = {
      items: dtos,
      start: getDate(changedDateRange.start),
      end: getDate(changedDateRange.end),
      customer_id: customerId,
      today: getDate(today),
    };

    loadingStart();
    requestPUT(apiUrlScheduled, requestData, csrftoken)
      .then(result => {
        alert(`Updated daily schedules: ${result.count}`);

        // Refetch all events from API
        calendar.removeAllEvents();
        calendar.refetchEvents();
        addFirstDeliveryDateBackgroundEvent();
      })
      .catch(error => alert(`An error occurred, try again.`))
      .finally(() => loadingEnd());
  }

  const calendar = new FullCalendar.Calendar(calendarEl, {
    timeZone: 'local',
    plugins: ['interaction', 'dayGrid'],
    customButtons: {
      saveButton: {
        text: 'Save changes',
        click: () => saveChanges(),
      }
    },
    header: {
      left: 'title',
      center: 'saveButton',
      right: 'today prev,next',
    },
    droppable: true,
    editable: true,
    // eventLimit: true, // when too many events in a day, show the popover
    eventSources: [
      getAssignedEvents,
      getScheduledEvents,
    ],
    /**
     * Function which define order of items
     * Order defined in mealsOrder variable
     */
    eventOrder: (event1, event2) => {
      const order1 = mealsOrder.indexOf(event1.extendedProps.type);
      const order2 = mealsOrder.indexOf(event2.extendedProps.type);
      return order1 > order2 ? 1 : -1;
    },
    /**
     * When event dropped from outside, set some props to nice display
     * @param event - fc event object
     */
    eventReceive: ({event}) => {
      const type = event.extendedProps.type;
      event.setProp('title', type);
      event.setProp('classNames', `scheduled-meal ${type} custom`);
      event.setExtendedProp('custom', true);

      updateChangedDateRange(event.start);
    },
    /**
     * When event dropped from one date to another, set "custom" property to true
     * @param oldEvent - old fc event object
     * @param event - new fc event object
     */
    eventDrop: ({oldEvent, event}) => {
      event.setExtendedProp('custom', true);
      updateChangedDateRange(event.start);
      updateChangedDateRange(oldEvent.start);
    },
    /**
     * When event dropped outside, on trash icon, remove this.
     * @param event - fc event object
     * @param jsEvent - javascript event
     */
    eventDragStop: function ({event, jsEvent}) {
      const ofs = trash.offset();

      const x1 = ofs.left;
      const x2 = ofs.left + trash.outerWidth(true);
      const y1 = ofs.top;
      const y2 = ofs.top + trash.outerHeight(true);

      if (
        jsEvent.pageX >= x1 && jsEvent.pageX <= x2 &&
        jsEvent.pageY >= y1 && jsEvent.pageY <= y2
      ) {
        updateChangedDateRange(event.start);
        event.remove();
      }
    },
    /**
     * Add default dishes count to each column header
     * We add default dishes count only for days, where count != undefined.
     * This is done in order not to show 0 on weekends.
     *
     * @param date
     * @returns {string|*}
     */
    columnHeaderHtml: function (date) {
      const day = date.getDay();
      const dayName = date.toString().split(' ')[0];
      const dishesCount = defaultWeeklySchedule[day];

      if (dishesCount >= 0) {
        return (
          `${dayName}</br>` +
          `<span class="dishes-count">${dishesCount} dishes</span>`
        );
      }
      return dayName;
    },
    /**
     * Calculate, can user drop new event or not.
     *
     * We implement the following restrictions:
     *  1) We forbid drop if at least one dish is already scheduled for this day.
     *  2) We forbid drop if it is Saturday or Sunday.
     *  3) We forbid drop if this is a date that is lower than the current one.
     *  4) We forbid drop if this is a date that is lower than first_delivery_date
     *
     * @param dropInfo information about new destination.
     * @returns {boolean} allow drop or not
     */
    eventAllow: function (dropInfo) {
      if (assignedDates.has(dropInfo.startStr)) {
        return false;
      }
      if ([0, 6].includes(dropInfo.start.getDay())) {
        return false;
      }
      if (dropInfo.start < firstDeliveryDate) {
        return false;
      }
      return dropInfo.start >= today;
    }
  });

  /* Initialize droppable elements inside droppable container. */
  new FullCalendarInteraction.Draggable(draggableContainerEl, {
    itemSelector: draggableItemSelector,
  });

  addFirstDeliveryDateBackgroundEvent();

  calendar.render();
}

