# page.py
from option import Option

class Page:
    def __init__(self, slash="", bot_name="Sniper King", title="", info="", options=[], expects_text=False):
        """
        Initializes the Page object with the provided parameters.

        Args:
            slash (str): The command or slash for the page (e.g., "menu", "channels").
            bot_name (str): The name of the bot (e.g., "Sniper King").
            title (str): The title of the page.
            info (str): The information displayed on the page.
            options (list): A list of options (e.g., buttons or actions) for the page.
            expects_text (bool): Whether this page expects a text input from the user.
        """
        self.title = title
        self.info = info
        self.slash = slash
        self.bot_name = bot_name
        self.options = options
        self.expects_text = expects_text  # If True, this page expects text input (like channel name)
        self.pending_text_action = None  # Action to take when text is input (e.g., adding a channel)
        self.invalid_input = False
        self.visible_options = []

    def display(self):
        """
        Displays the current page, including the title, info, options, and invalid input message if applicable.

        Returns:
            str: The formatted string representing the current page to be shown to the user.
        """
        options = ""
        invalid = ""

        # Only display options, not gaps, for numeric input
        index = 1
        for option in self.options:
            if not isinstance(option, Option):
                options += option.display()
            else:
                self.visible_options.append(option)
                options += option.display(index) + "\n"  # Display the actual option
                index += 1

        if self.invalid_input:
            self.invalid_input = False
            invalid = "\n❌ **Invalid Input** __Please enter a valid option.__"
        return (
f"""
**{self.bot_name}**

**{self.title}** /{self.slash} 
__{self.info}__

{options}{invalid}
""")

    def handle_input(self, user_input):
        """
        Handles the input provided by the user. This method processes whether the page expects text input 
        or numeric option input and takes appropriate action.

        Args:
            user_input (str): The input provided by the user, either a number or text.
        """
        if self.expects_text:
            # If the page expects text input, handle it (e.g., adding a channel)
            if self.pending_text_action:
                self.pending_text_action(user_input)
            self.expects_text = False  # Reset after handling the input
        else:
            self.handle_option_input(user_input)

    def handle_option_input(self, user_input):
        """
        Processes the numeric input provided by the user and executes the corresponding option.

        Args:
            user_input (str): The input provided by the user, expected to be a number corresponding to an option.
        """
        try:
            # Handle numeric option input (map to visible options)
            choice = int(user_input)
            if 1 <= choice <= len(self.visible_options):
                # Execute the selected option's action
                self.visible_options[choice - 1].execute()
            else:
                self.invalid_input = True
        except ValueError:
            self.invalid_input = True