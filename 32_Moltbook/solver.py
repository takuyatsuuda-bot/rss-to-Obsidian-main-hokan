import re

WORD_TO_NUM = {
    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
    'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14,
    'fifteen': 15, 'sixteen': 16, 'seventeen': 17, 'eighteen': 18,
    'nineteen': 19, 'twenty': 20, 'thirty': 30, 'forty': 40,
    'fifty': 50, 'sixty': 60, 'seventy': 70, 'eighty': 80,
    'ninety': 90, 'hundred': 100,
    # Common obfuscation fixes
    'thre': 3, 
    'fourten': 14, 'fiften': 15, 'sixten': 16, 'seventen': 17, 'eighten': 18, 'nineten': 19,
    'thirten': 13
}

OPS = {
    'multipl': '*', 'times': '*', 'product': '*',
    'subtract': '-', 'minus': '-', 'less': '-', 'slow': '-', 'reduce': '-',
    'add': '+', 'plus': '+', 'total': '+', 'adds': '+', 'ads': '+'
}

def solve_challenge_v3(challenge_text):
    print(f"Original Challenge: {challenge_text}")
    # 1. Clean Up: Remove non-alpha chars to read words clearly
    # But keep spaces to separate words? Or just concat?
    # The challenge looks like: "A] lOo.oBbSsTtErr LoOo^bS tErr Cl@aWw ExErTtSs FfOoRrTtY] nEeWwToOnSs..."
    # Cleaning strategy: Keep only letters and spaces.
    
    # Cleaning strategy: 
    # 1. Remove non-alpha chars (keep spaces)
    clean = re.sub(r"[^a-zA-Z\s]", "", challenge_text).lower()
    
    # 2. Collapse repeated characters: "ffoorrtty" -> "forty"
    # This is tricky because some words have double letters (tree, three, etc.)
    # But looking at the challenge: "lOo.oBbSsTtErr" -> "lobster"
    # It seems to be simply repeating each char 1-2 times?
    # Let's try a simple approach: if a char varies from previous, keep it.
    # But wait: "three" has 'ee'. "add" has 'dd'.
    # However, "ffoorrtty" has 2 of EVERYTHING.
    
    # Let's try aggressive fuzzy matching instead of perfect cleaning.
    # Check if a word "contains" the target number word in sequence.
    
    # Actually, let's just deduplicate adjacent characters first, 
    # knowing that we might kill legitimate double letters, but most number words don't have them
    # except "three", "thirteen", "fifteen", "eighteen".
    
    def dedup(text):
        if not text: return ""
        res = text[0]
        for char in text[1:]:
            if char != res[-1]:
                res += char
        return res
        
    clean_dedup = dedup(clean)
    print(f"Deduped Text: {clean_dedup}")
    
    # NEW: Merge separated syllables? "twen ty" -> "twenty", "th re" -> "three"
    # Or just remove spaces completely? 
    # If we remove spaces, we get "alobsterusesclawforcetwentythreenotons..."
    # Then we can search for number words inside that long string?
    # That might be safer given the fragmentation.
    
    clean_nospace = clean_dedup.replace(" ", "")
    print(f"NoSpace Text: {clean_nospace}")
    
    # 2. Extract Numbers and Ops
    # Search for number words in the nospace string
    # We need to maintain order. 
    # Let's iterate through the string or find all occurrences?
    
    # Mapping of index found -> value
    found_items = []
    
    for word, val in WORD_TO_NUM.items():
        # Find all start indices of this word
        start = 0
        while True:
            idx = clean_nospace.find(word, start)
            if idx == -1: break
            found_items.append( (idx, val, 'num') )
            start = idx + 1
            
    for op_key, op_sym in OPS.items():
         start = 0
         while True:
            idx = clean_nospace.find(op_key, start)
            if idx == -1: break
            found_items.append( (idx, op_sym, 'op') )
            start = idx + 1
            
    # Sort by index
    found_items.sort(key=lambda x: x[0])
    
    # Filter out overlaps. Prioritize longer matches? 
    # Current list has all occurrences.
    # If we have "fourten" at idx 0 (len 7) and "four" at idx 0 (len 4) and "ten" at idx 4 (len 3).
    # We want "fourten".
    # So we should filter: if an item is fully contained within another covering item, drop it.
    
    # Re-find with Length info
    found_items = []
    
    for word, val in WORD_TO_NUM.items():
        start = 0
        while True:
            idx = clean_nospace.find(word, start)
            if idx == -1: break
            found_items.append( {'idx': idx, 'len': len(word), 'val': val, 'type': 'num'} )
            start = idx + 1
            
    for op_key, op_sym in OPS.items():
         start = 0
         while True:
            idx = clean_nospace.find(op_key, start)
            if idx == -1: break
            found_items.append( {'idx': idx, 'len': len(op_key), 'val': op_sym, 'type': 'op'} )
            start = idx + 1
            
    # Sort by Index ASC, then Length DESC
    found_items.sort(key=lambda x: (x['idx'], -x['len']))
    
    final_items = []
    last_end = -1
    
    for item in found_items:
        start = item['idx']
        end = start + item['len']
        
        # If this item starts after the last accepted item ended, take it.
        # Since we sorted by length DESC for same start, we pick the longest first.
        # But wait, what if "twentyone" and "twenty"? 
        # "twentyone" starts at 0, len 9. "twenty" starts at 0, len 6.
        # We pick "twentyone". last_end becomes 9.
        # Next item "twenty" starts at 0 < 9, skip.
        # Next item "one" starts at 6 < 9, skip.
        
        if start >= last_end:
            final_items.append(item)
            last_end = end
            
    # Extract values
    nums = []
    ops = []
    merged_nums = []
    
    # Convert to list of (val, type)
    token_stream = [ (x['val'], x['type']) for x in final_items ]
    
    i = 0
    while i < len(token_stream):
        val, type_ = token_stream[i]
        
        if type_ == 'num':
            n = val
            # Check next for compound
            if i + 1 < len(token_stream):
                next_val, next_type = token_stream[i+1]
                if next_type == 'num':
                    if n >= 20 and n % 10 == 0 and next_val < 10:
                        n += next_val
                        i += 1 
            merged_nums.append(n)
        elif type_ == 'op':
            ops.append(val)
            
        i += 1
        
    nums = merged_nums
    
    # Debug print
    print(f"Found Nums (nospace): {nums}")
    print(f"Found Ops (nospace): {ops}")
    
    # If this fails, we fall back to the old split method? 
    # No, let's trust this for now. The fragmentation "twen ty" is the main enemy.
    
    words = [] # Disable old loop logic
    clean_final = "" # Disable old loop logic reference
        
    print(f"Found Nums: {nums}")
    print(f"Found Ops: {ops}")
    
    if not nums: return 0.0
    
    # 3. Calculate
    # Usually it's "A does X ... and ... B does Y ... Total?"
    # Or "X minus Y"
    
    # If explicit op found, use it
    op = '+' # Default to add if "total" or "add"
    if ops:
        op = ops[0]
        
    res = float(nums[0])
    for n in nums[1:]:
        if op == '+': res += n
        elif op == '-': res -= n
        elif op == '*': res *= n
        
    return res
