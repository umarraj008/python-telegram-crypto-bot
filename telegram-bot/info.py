# info.py

class Info:
    def __init__(self, text):
        """
        Initializes an Info object with the given text and an optional action.

        Args:
            text (str): The text content to be displayed as information.
            action (callable, optional): A function or action to be executed. Defaults to None.
        """
        self.text = text

    def display(self):
        """
        Returns the text of the Info object.

        Returns:
            str: The text content stored in the Info object.
        """
        return self.text