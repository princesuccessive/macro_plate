/** Function to group items by one attribute */
function groupItems(items, attrGetter) {
  const groups = {};
  items.forEach(item => {
    const groupName = attrGetter(item);
    if (!groups[groupName]) {
      groups[groupName] = []
    }
    groups[groupName].push(item);
  });
  return groups;
}

/** Vue instance for the Configurator on the daily_menu page */
new Vue({
  el: '#congifurator',
  delimiters: ['[[', ']]'],
  components: {
    vuedraggable,
  },
  data: {
    /** Meal selected in dropdown */
    selectedMeal: null,
    /** Grouped assigned meals by planTypeId */
    groupedAssignedMeals: {},
    /** Map with plan type info { id: PlanType } */
    planTypes: {}
  },
  mounted() {
    // Sort assigned meals by order
    const ordered = ASSIGNED_MEALS.sort((a, b) => a.order - b.order);

    // Convert assigned meals to meals
    const assignedMeals = []
    ordered.forEach(assignedItem => {
      const meal = MEALS.find(m => m.id === assignedItem.meal_id);
      if (meal) {
        assignedMeals.push(meal);
      }
    });

    // Group assigned meals
    this.groupedAssignedMeals = groupItems(
      assignedMeals,
      (meal) => meal.plan_type.id,
    );

    // Create map of all plan types
    this.planTypes = {}
    MEALS.forEach((meal) => {
      const plan = meal.plan_type;
      this.$set(this.planTypes, plan.id, plan);
    });
  },
  watch: {
    /**
     * Refresh select when assigned meals changed.
     * It's needed to remove already used options.
     */
    groupedAssignedMeals: {
      deep: true,
      handler() {
        this.$nextTick(() => DROPDOWN.selectpicker('refresh'));
      }
    },
    /**
     * When meal selected in dropdown, add this to assigned meals and clear
     */
    selectedMeal(meal) {
      if (meal) {
        this.addMeal(meal);
        this.selectedMeal = null;
      }
    }
  },
  computed: {
    /** Get list of all plan type ids to support constant order in plans list */
    planTypesIds() {
      return Object.keys(this.planTypes);
    },
    /** Get flat structure of assigned meals instead of groped */
    assignedMeals() {
      const meals = [];
      Object.values(this.groupedAssignedMeals).forEach(group => meals.push(...group));
      return meals;
    },
    /** Get only not assigned meals */
    notAssignedMeals() {
      return MEALS.filter(m => {
        return !this.assignedMeals.find(i => i.id === m.id)
      });
    },
    /** Get grouped not assigned meals by plan type name */
    groupedNotAssignedMeals() {
      return groupItems(
        this.notAssignedMeals,
        (meal) => meal.plan_type.id,
      );
    },
  },
  methods: {
    /** Add new assigned meal to the list */
    addMeal(meal) {
      const groupId = meal.plan_type.id;

      if (!this.groupedAssignedMeals[groupId]) {
        this.$set(this.groupedAssignedMeals, groupId, []);
      }

      this.groupedAssignedMeals[groupId].push(meal);
    },
    /** Delete assigned meal from the list */
    deleteMeal(meal) {
      const groupName = meal.plan_type.id;
      const mealsInGroup = this.groupedAssignedMeals[groupName];
      this.groupedAssignedMeals[groupName] = mealsInGroup.filter(i => i.id !== meal.id)
    },
    /** Save assigned meals on server */
    save() {
      // Convert internal structure to API structure and add ORDER field
      const assignedItems = [];
      Object.values(this.groupedAssignedMeals).forEach(groupItems => {
        groupItems.forEach((meal, index) => {
          const oldAssignedMeal = ASSIGNED_MEALS.find(i => i.meal_id === meal.id)

          assignedItems.push({
            id: oldAssignedMeal?.id || 0,
            meal_id: meal.id,
            order: index,
          })
        })
      })

      $.ajaxSetup({
        beforeSend: function (xhr) {
          xhr.setRequestHeader("X-CSRFToken", CSRF_TOKEN);
        }
      });

      $.ajax({
        type: 'POST',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        url: SAVE_URL,
        data: JSON.stringify({
          items: assignedItems,
        }),
        success: (response) => location.reload(),
        error: (err) => alert(err),
      });
    },
    getPlanName(id) {
      return (this.planTypes[id] || {}).name || 'Unknown';
    }
  }
})
