# option.py

class Option:
    def __init__(self, text, action):
        """
        Initializes an Option object with the given text and associated action.

        Args:
            text (str): The text displayed for the option.
            action (callable): The action to be executed when the option is selected.
        """
        self.text = text
        self.action = action
        self.number_emojis = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

    def display(self, index):
        """
        Displays the option with its associated emoji and text.

        Args:
            index (int): The index of the option to determine the corresponding emoji.

        Returns:
            str: A formatted string with the emoji and the option's text.
        """
        return f"{self.number_emojis[index]} {self.text}"

    def execute(self):
        """
        Executes the action associated with the option.

        This function calls the action that was provided during initialization.
        """
        if self.action:
            self.action()