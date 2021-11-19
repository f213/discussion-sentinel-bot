from typing import List

import emoji


class Labels:
    LABELS = [
    ]

    def __init__(self, text: str):
        self.text = text

    def __call__(self) -> List[str]:
        return self.get_emoji_label()

    def get_emoji_label(self) -> List[str]:
        emoji_count = len(emoji.emoji_lis(self.text))

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
