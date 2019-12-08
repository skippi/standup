from standup.post import message_is_formatted


def test_message_is_formatted_accepts_plain() -> None:
    msg = (
        "Yesterday I: Did nothing!\n"
        "Today I will: Work on my discord bot!\n"
        "Potential hard problems: None!"
    )

    assert message_is_formatted(msg)


def test_message_is_formatted_fails_improper_newlines() -> None:
    msg = (
        "Yesterday I: did nothing!"
        "Today I will: Work on my discord bot!"
        "Potential hard problems: None!"
    )

    assert not message_is_formatted(msg)
