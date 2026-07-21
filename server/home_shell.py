from users_db import UsersDB


def ask(prompt: str) -> str:
    return input(prompt).strip()


def main():
    db = UsersDB()
    print("=== Kung-Fu Chess — Home ===")
    print("1) Register")
    print("2) Login")
    print("3) Quit")

    choice = ask("> ")

    if choice == "1":
        user = ask("username: ")
        pwd = ask("password: ")
        ok, msg = db.register(user, pwd)
        print(msg)
        if ok:
            print("(you can now choose Login)")

    elif choice == "2":
        user = ask("username: ")
        pwd = ask("password: ")
        ok, msg, elo = db.login(user, pwd)
        print(msg)
        if ok:
            print(f"Welcome, {user}! Your ELO is {elo}.")
            # Next steps (later today): Play / matchmaking / connect to game server
            print("(Day 3 next: ELO update after games + connect to server)")

    elif choice == "3":
        print("bye")
    else:
        print("unknown choice")


if __name__ == "__main__":
    main()