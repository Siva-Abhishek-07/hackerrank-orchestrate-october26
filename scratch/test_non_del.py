import re, csv

non_del = [
    (r'\bupdate\b.*\b(phone|email|address|name|surname|number)\b', 'update...field'),
    (r'\b(phone|email|address|name|surname|number)\b.*\bupdate\b', 'field...update'),
    (r'\bcorrect\b', 'correct'),
    (r'\bfix\b.*\b(name|email|phone|address)\b', 'fix...field'),
    (r'\bchange\b.*\b(email|phone|address|name)\b', 'change...field'),
    (r'\bdownload\b', 'download'),
    (r'\bexport\b', 'export'),
    (r'\bcopy of\b', 'copy of'),
    (r'\bportable\b', 'portable'),
    (r'\bkeep the account\b', 'keep account'),
    (r'\bleave the account\b', 'leave account'),
    (r'\bactive\b', 'active'),
    (r'\bcontinue using\b', 'continue using'),
    (r'\bkeep my account\b', 'keep my account'),
    (r'\baccess\b.*\bdata\b', 'access data'),
    (r'\baccess request\b', 'access request'),
    (r'\bopt.out\b.*\bmarketing\b', 'opt out marketing'),
    (r'\bunsubscribe\b', 'unsubscribe'),
    (r'\binvoices?\b.*\bleave\b', 'invoice leave'),
    (r'\bleave.*\bprofile\b', 'leave profile'),
    (r'\bmisspelled\b', 'misspelled'),
    (r'\bout of date\b.*\bnumber\b', 'out of date number'),
    (r'\bnew.*\bnumber\b', 'new number'),
]

with open('dataset/sample_deletion_requests.csv', newline='', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        t = r['request_text'].lower()
        matched = [name for p, name in non_del if re.search(p, t)]
        if matched:
            print(f"{r['case_id']}: matched {matched}")
            print(f"  Text: {r['request_text']}")
