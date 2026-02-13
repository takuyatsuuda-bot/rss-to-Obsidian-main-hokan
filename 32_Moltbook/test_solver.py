from solver import solve_challenge_v3

challenge = "A] lO^bSt-Er umm sS tTt ErS lOoOoobsssster uSeS cL]aW fO^rCe tW/eN tY tH rEe noOotOnS, aNd- thE oThEr cL]aW aDdS fOuR tEeN noOtOnS - wH/aT] iS tO^tAl fOrCe?"

print(f"Testing Challenge:\n{challenge}\n")

try:
    result = solve_challenge_v3(challenge)
    print(f"\nResult: {result}")
except Exception as e:
    print(f"Error: {e}")
