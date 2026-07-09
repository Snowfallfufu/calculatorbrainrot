"""
Beat the Dealer Calculator (Blackjack + Centered Popup Edition)
--------------------------------------------------------------------
A fun, PLAY-MONEY-ONLY calculator game.

Rules:
  - Tap digits/operators on the on-screen keypad to build an expression.
  - Hit "=" to lock in the calculation. A POPUP appears (centered on the
    window) with two choices:
      a) Pay 25 coins to unlock instantly, or
      b) Play ONE round of Blackjack against the dealer.
         - You may only play Blackjack ONCE per calculation.
         - Win / Blackjack -> unlocks for FREE.
         - Push (tie)      -> the Answer Locked popup reappears (pay-only,
                               since your one Blackjack try is used).
         - Lose / Bust     -> you are automatically charged 25 coins, and
                               the Answer Locked popup reappears (pay-only).
  - The revealed answer is intentionally off by 1, just for fun.

No real money, no real payments, no network calls. Everything is local
and just for entertainment. Run this file directly in PyCharm
(Run > Run 'beat_the_dealer_calculator').
"""

import tkinter as tk
from tkinter import messagebox
import random

STARTING_BALANCE = 100
UNLOCK_COST = 25

RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]


def card_value(rank):
    if rank in ("J", "Q", "K"):
        return 10
    if rank == "A":
        return 11
    return int(rank)


def hand_value(cards):
    total = sum(card_value(c) for c in cards)
    aces = cards.count("A")
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total


def draw_card():
    return random.choice(RANKS)


def center_on_parent(win, parent, width, height):
    win.update_idletasks()
    px = parent.winfo_rootx()
    py = parent.winfo_rooty()
    pw = parent.winfo_width()
    ph = parent.winfo_height()
    x = px + (pw - width) // 2
    y = py + (ph - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")


class CalculatorGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.geometry("420x600")
        self.resizable(False, False)
        self.configure(bg="#1e1e2e")

        self.balance = STARTING_BALANCE
        self.expression = ""
        self.computed_answer = None
        self.unlocked = False
        self.dealer_attempt_used = False

        self._build_ui()

    # ---------- UI ----------
    def _build_ui(self):
        title = tk.Label(
            self, text="Calculator",
            font=("Helvetica", 18, "bold"), fg="#f5c542", bg="#1e1e2e"
        )
        title.pack(pady=(15, 2))


        self.balance_var = tk.StringVar()
        self._update_balance_label()
        tk.Label(
            self, textvariable=self.balance_var,
            font=("Helvetica", 13, "bold"), fg="#4caf50", bg="#1e1e2e"
        ).pack(pady=(0, 10))

        self.expr_var = tk.StringVar(value="0")
        tk.Label(
            self, textvariable=self.expr_var,
            font=("Helvetica", 20), fg="white", bg="#2a2a3d",
            anchor="e", padx=10, width=18, height=1
        ).pack(pady=(0, 8))

        self.result_var = tk.StringVar(value="🔒 Locked")
        tk.Label(
            self, textvariable=self.result_var,
            font=("Helvetica", 22, "bold"), fg="#f5c542", bg="#1e1e2e",
            wraplength=380, justify="center"
        ).pack(pady=10)

        keypad_frame = tk.Frame(self, bg="#1e1e2e")
        keypad_frame.pack(pady=5)

        buttons = [
            ("7", 0, 0), ("8", 0, 1), ("9", 0, 2), ("/", 0, 3),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2), ("*", 1, 3),
            ("1", 2, 0), ("2", 2, 1), ("3", 2, 2), ("-", 2, 3),
            ("0", 3, 0), (".", 3, 1), ("C", 3, 2), ("+", 3, 3),
            ("(", 4, 0), (")", 4, 1), ("⌫", 4, 2), ("=", 4, 3),
        ]

        for label, row, col in buttons:
            color = "#3b3b52"
            if label == "=":
                color = "#3b82f6"
            elif label in ("C", "⌫"):
                color = "#ef4444"
            elif label in ("+", "-", "*", "/", "(", ")"):
                color = "#6b6b8a"

            tk.Button(
                keypad_frame, text=label, font=("Helvetica", 14, "bold"),
                width=5, height=2, bg=color, fg="white",
                activebackground="#525278",
                command=lambda l=label: self.on_key(l)
            ).grid(row=row, column=col, padx=4, pady=4)

        self.status_var = tk.StringVar(value="")
        tk.Label(
            self, textvariable=self.status_var,
            font=("Helvetica", 10), fg="#9aa0a6", bg="#1e1e2e",
            wraplength=380, justify="center"
        ).pack(pady=(15, 5))

        reset_btn = tk.Button(
            self, text="Reset Balance", font=("Helvetica", 9),
            bg="#374151", fg="white", command=self.reset_balance
        )
        reset_btn.pack(pady=(10, 5))

    def _update_balance_label(self):gi
        self.balance_var.set(f"Coin Balance: {self.balance} 🪙")

    # ---------- Keypad logic ----------
    def on_key(self, key):
        if key == "C":
            self.expression = ""
            self.expr_var.set("0")
            self._lock_again()
            return

        if key == "⌫":
            self.expression = self.expression[:-1]
            self.expr_var.set(self.expression if self.expression else "0")
            return

        if key == "=":
            self.calculate()
            return

        self.expression += key
        self.expr_var.set(self.expression)

    def _lock_again(self):
        self.unlocked = False
        self.computed_answer = None
        self.dealer_attempt_used = False
        self.result_var.set("🔒 Locked")
        self.status_var.set("")

    def calculate(self):
        expr = self.expression.strip()
        if not expr:
            messagebox.showwarning("Empty input", "Tap some numbers first.")
            return

        try:
            allowed = set("0123456789+-*/(). ")
            if not set(expr) <= allowed:
                raise ValueError("Only numbers and + - * / ( ) are allowed.")
            answer = eval(expr, {"__builtins__": {}}, {})
        except Exception:
            messagebox.showerror("Invalid expression", "That's not a valid expression. Try again.")
            return

        self.computed_answer = answer
        self.unlocked = False
        self.dealer_attempt_used = False

        self.result_var.set("🔒 Locked")
        self.status_var.set("Answer locked.")

        # Immediately pop up the unlock choice
        self.show_unlock_popup()

    def _format(self, value):
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)

    def _reveal(self):
        # Revealed answer is intentionally off by 1, just for fun
        wrong_answer = self.computed_answer + 1
        self.unlocked = True
        self.result_var.set(f"✅ Answer: {self._format(wrong_answer)}")

    def show_unlock_popup(self):
        if self.unlocked or self.computed_answer is None:
            return
        UnlockPopup(self, show_dealer_option=not self.dealer_attempt_used)

    def pay_to_unlock(self):
        if self.unlocked or self.computed_answer is None:
            return
        if self.balance < UNLOCK_COST:
            messagebox.showinfo("Not enough coins", "You don't have enough coins.")
            return

        self.balance -= UNLOCK_COST
        self._update_balance_label()
        self._reveal()
        self.status_var.set(f"Paid {UNLOCK_COST} coins to unlock.")

    # ---------- Blackjack ----------
    def start_blackjack(self):
        if self.unlocked or self.computed_answer is None:
            return
        if self.dealer_attempt_used:
            return

        self.dealer_attempt_used = True
        BlackjackWindow(self)

    def resolve_blackjack(self, outcome):
        """outcome: 'win', 'push', or 'lose'"""
        if outcome == "win":
            self._reveal()
            self.status_var.set("🎉 Blackjack win! Answer unlocked for free.")
        elif outcome == "push":
            self.status_var.set("🤝 Push (tie). No charge, but still locked.")
            self.show_unlock_popup()  # pay-only now, since attempt is used
        else:  # lose
            charge = min(UNLOCK_COST, self.balance)
            self.balance -= charge
            if self.balance < 0:
                self.balance = 0
            self._update_balance_label()
            self.status_var.set(f"😞 You lost to the dealer. Charged {charge} coins automatically. Still locked.")

            if self.balance <= 0:
                messagebox.showinfo("Out of coins", "You're out of coins! Resetting balance for more fun.")
                self.reset_balance()

            self.show_unlock_popup()  # pay-only now, since attempt is used

    def reset_balance(self):
        self.balance = STARTING_BALANCE
        self._update_balance_label()
        messagebox.showinfo("Balance reset", f"Balance reset to {STARTING_BALANCE} coins.")


class UnlockPopup(tk.Toplevel):
    """Popup shown after calculating (or after a Blackjack loss/push),
    offering Pay, and Beat the Dealer only if the attempt hasn't been used."""

    def __init__(self, app: CalculatorGame, show_dealer_option: bool):
        super().__init__(app)
        self.app = app
        self.title("Answer Locked 🔒")
        self.resizable(False, False)
        self.configure(bg="#1e1e2e")
        self.transient(app)

        width = 340
        height = 260 if show_dealer_option else 200

        tk.Label(
            self, text="🔒 Your answer is locked!", font=("Helvetica", 15, "bold"),
            fg="#f5c542", bg="#1e1e2e"
        ).pack(pady=(20, 10))

        tk.Label(
            self, text="Choose how to unlock it:", font=("Helvetica", 11),
            fg="white", bg="#1e1e2e"
        ).pack(pady=(0, 15))

        pay_btn = tk.Button(
            self, text=f"💰 Pay {UNLOCK_COST} coins", font=("Helvetica", 12, "bold"),
            bg="#f97316", fg="white", activebackground="#ea580c", width=24,
            command=self._choose_pay
        )
        pay_btn.pack(pady=6)

        if show_dealer_option:
            dealer_btn = tk.Button(
                self, text="🃏 Beat the Dealer — Blackjack (1 try)", font=("Helvetica", 12, "bold"),
                bg="#8b5cf6", fg="white", activebackground="#7c3aed", width=24,
                command=self._choose_dealer
            )
            dealer_btn.pack(pady=6)

        tk.Button(
            self, text="Maybe later", font=("Helvetica", 9),
            bg="#374151", fg="white", command=self.destroy
        ).pack(pady=(15, 5))

        center_on_parent(self, app, width, height)
        self.grab_set()  # modal (set after positioning so it doesn't jump)

    def _choose_pay(self):
        self.destroy()
        self.app.pay_to_unlock()

    def _choose_dealer(self):
        self.destroy()
        self.app.start_blackjack()


class BlackjackWindow(tk.Toplevel):
    """A simple one-round Blackjack game: player vs dealer, dealer hits to 17."""

    def __init__(self, app: CalculatorGame):
        super().__init__(app)
        self.app = app
        self.title("Blackjack — Beat the Dealer")
        self.resizable(False, False)
        self.configure(bg="#0f3d2e")
        self.protocol("WM_DELETE_WINDOW", self._on_close_attempt)

        self.player_cards = [draw_card(), draw_card()]
        self.dealer_cards = [draw_card(), draw_card()]
        self.game_over = False

        self._build_ui()
        self._refresh(reveal_dealer=False)

        center_on_parent(self, app, 380, 420)
        self.grab_set()  # modal

        # Natural blackjack check
        if hand_value(self.player_cards) == 21:
            self._finish()

    def _build_ui(self):
        tk.Label(
            self, text="🂡 Blackjack — 1 Attempt Only", font=("Helvetica", 15, "bold"),
            fg="#f5c542", bg="#0f3d2e"
        ).pack(pady=(15, 10))

        self.dealer_label = tk.Label(
            self, text="", font=("Helvetica", 13), fg="white", bg="#0f3d2e", justify="center"
        )
        self.dealer_label.pack(pady=10)

        self.player_label = tk.Label(
            self, text="", font=("Helvetica", 13), fg="white", bg="#0f3d2e", justify="center"
        )
        self.player_label.pack(pady=10)

        self.status_label = tk.Label(
            self, text="Hit or Stand?", font=("Helvetica", 12, "bold"),
            fg="#f5c542", bg="#0f3d2e"
        )
        self.status_label.pack(pady=15)

        btn_frame = tk.Frame(self, bg="#0f3d2e")
        btn_frame.pack(pady=10)

        self.hit_btn = tk.Button(
            btn_frame, text="Hit", font=("Helvetica", 12, "bold"),
            width=10, bg="#3b82f6", fg="white", command=self.hit
        )
        self.hit_btn.grid(row=0, column=0, padx=8)

        self.stand_btn = tk.Button(
            btn_frame, text="Stand", font=("Helvetica", 12, "bold"),
            width=10, bg="#ef4444", fg="white", command=self.stand
        )
        self.stand_btn.grid(row=0, column=1, padx=8)

        self.close_btn = tk.Button(
            self, text="Close", font=("Helvetica", 10),
            bg="#374151", fg="white", command=self.destroy, state="disabled"
        )
        self.close_btn.pack(pady=(15, 5))

    def _on_close_attempt(self):
        if not self.game_over:
            messagebox.showwarning("Finish the round", "Finish this Blackjack round first — it's your only attempt!")
            return
        self.destroy()

    def _refresh(self, reveal_dealer):
        if reveal_dealer:
            dealer_text = f"Dealer: {' '.join(self.dealer_cards)}  (value: {hand_value(self.dealer_cards)})"
        else:
            dealer_text = f"Dealer: {self.dealer_cards[0]}  ??"

        self.dealer_label.config(text=dealer_text)
        self.player_label.config(
            text=f"You: {' '.join(self.player_cards)}  (value: {hand_value(self.player_cards)})"
        )

    def hit(self):
        if self.game_over:
            return
        self.player_cards.append(draw_card())
        value = hand_value(self.player_cards)
        self._refresh(reveal_dealer=False)

        if value > 21:
            self._finish()
        elif value == 21:
            self.stand()

    def stand(self):
        if self.game_over:
            return
        self._finish()

    def _finish(self):
        self.game_over = True
        self.hit_btn.config(state="disabled")
        self.stand_btn.config(state="disabled")

        player_value = hand_value(self.player_cards)

        if player_value > 21:
            self._refresh(reveal_dealer=True)
            self.status_label.config(text="💥 You busted! Dealer wins.")
            outcome = "lose"
        else:
            # Dealer plays: hits until 17+
            while hand_value(self.dealer_cards) < 17:
                self.dealer_cards.append(draw_card())

            self._refresh(reveal_dealer=True)
            dealer_value = hand_value(self.dealer_cards)

            if dealer_value > 21:
                self.status_label.config(text="🎉 Dealer busts! You win!")
                outcome = "win"
            elif player_value > dealer_value:
                self.status_label.config(text=f"🎉 You win! {player_value} vs {dealer_value}")
                outcome = "win"
            elif player_value < dealer_value:
                self.status_label.config(text=f"😞 Dealer wins. {dealer_value} vs {player_value}")
                outcome = "lose"
            else:
                self.status_label.config(text=f"🤝 Push! Both have {player_value}")
                outcome = "push"

        self.close_btn.config(state="normal")
        self.app.resolve_blackjack(outcome)


if __name__ == "__main__":
    app = CalculatorGame()
    app.mainloop()