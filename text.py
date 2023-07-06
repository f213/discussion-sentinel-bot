from typing import List, Optional

import emoji


class Labels:
    def __init__(self, text: Optional[str]) -> None:
        self.text = text

    def __call__(self) -> List[str]:
        return self.get_emoji_label()

    def get_emoji_label(self) -> List[str]:
        if self.text is None:
            return []

        emoji_count = len(emoji.emoji_list(self.text))

        if emoji_count == 0:
            return []

        if emoji_count == 1:
            return ['emoji']

        if emoji_count == 2:
            return ['two_emojies']

        return ['three_or_more_emojies']


if __name__ == '__main__':
    assert Labels('текст')() == []
    assert Labels('текст😁')() == ['emoji']
    assert Labels('😁текст😁')() == ['two_emojies']
    assert Labels('😁😁😁текст')() == ['three_or_more_emojies']
