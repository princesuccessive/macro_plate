`Pylama` checker for doc style
===========

Prepare usage

.. code-block:: bash

    pip install pydocstyle pylama pycodestyle

For checking the docstring configure additional linter `pydocstyle <http://www.pydocstyle.org/en/3.0.0/>`_
for utility `pylama` about file configuration is `pylama.ini <https://pylama.readthedocs.io/en/latest/#configuration-file>`_

`Information about pydocstyle messages <http://www.pydocstyle.org/en/3.0.0/error_codes.html>`_

Simple file example:

.. code-block:: bash

    # Common to all rules
    [pylama]
    linters = pydocstyle,pycodestyle
    format = pylint
    skip = */migrations*.py,*/.env/*,*/.venv/*,*/testing*.py,*/tests*.py
    ignore = D100,D105,D104,D203,D204,D205,D213,D301,D400,D406,D407,D413

    # Special rules for modules, folders or files
    [pylama:*/admin.py]
    ignore = D106

Simple usage:

.. code-block:: bash

   pylama <folder_name>
..

Example of console output with result of checking with (pylint) format:

.. code-block:: python
    :caption: D101 Missing docstring in public class

    class TasksConfig(AppConfig):
        name = 'tasks'


.. code-block:: python
    :caption: D401 First line should be in imperative mood; try rephrasing (found 'Custom')

    def formatted_billable_hours(self, obj):
        """Custom field for represent billable hours"""
        return obj.hours_summary().formatted_billable()

.. code-block:: python
    :caption: D210 No whitespaces allowed surrounding docstring text

    class TaskIDAutocomplete(AutocompleteQuerySetView):
        """Provide lookup for `Task` by `id` """
        model = Task
        ordering = '-id'
        field_lookup = 'icontains'
        filter_field = 'id'

.. code-block:: python
    :caption: D101 Missing docstring in public class [pydocstyle]

    class UserUpdateView(LoginRequiredMixin, UpdateView):
        fields = ['email', 'first_name', 'last_name', ]

        def get_success_url(self):
            return "{}?success=1".format(reverse("users:profile"))

        def get_object(self):
            return self.request.user

.. code-block:: python
    :caption: D200 One-line docstring should fit on one line with quotes

    class UsersAppDefaultConfig(AppConfig):
    """Default configuration for Users app
    """

        name = 'apps.users'
        verbose_name = 'Users'

.. code-block:: python
    :caption: D102 Missing docstring in public method

    def pre_social_login(self, request, sociallogin):
        verified_email = None
        verification = False

.. code-block:: python
    :caption: D212 Multi-line docstring summary should start at the first line [pydocstyle]

    def save_user(self, request, user, form):
        """
        Args:
            user (users.User): empty User instance
            form (CustomRegisterSerializer): Serializer filled with values
        """
        return super().save_user(request, user, form)


.. code-block:: python
    :caption: D106 Missing docstring in public nested class [pydocstyle]

    class UserFactory(factory.DjangoModelFactory):
        """Factory for generates test User model.

        There are required fields first_name, last_name, username and email.

        """

        class Meta:
            model = User
..

Additional you can comment `# noqa` in code and disable the checking message, like this:

.. code-block:: python
    :caption: Using `noqa`

    class ClassWithoutTesting(object): # noqa
        pass
..
