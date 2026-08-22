#!/usr/bin/env python3
'''
SolSniper Lead Capture System

Captures leads from various sources and creates GitHub issues for follow-up.
'''

import os
import json
import time
import requests
from dataclasses import dataclass
from typing import Optional


@dataclass
class Lead:
    source: str              # 'github', 'web', 'referral', 'organic'
    contact: str             # Telegram, email, Discord
    plan_interest: str       # 'founding', 'lifetime', 'monthly', 'free'
    experience: str = ''
    referral_code: str = ''
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class LeadCapture:
    '''Capture leads and create GitHub issues for sales follow-up'''
    
    def __init__(self, github_token: str, repo: str = 'ezequiellich44-cmd/SolSniper'):
        self.github_token = github_token
        self.repo = repo
        self.headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github+json',
            'User-Agent': 'solsniper-lead-capture'
        }
    
    def capture_lead(self, lead: Lead) -> Optional[int]:
        '''Create GitHub issue for lead'''
        title = f'[LEAD] {lead.source} - {lead.plan_interest} - {lead.contact[:30]}'
        
        body = f'''## 🎯 New Lead Captured

**Source:** {lead.source}
**Contact:** {lead.contact}
**Plan Interest:** {lead.plan_interest}
**Experience:** {lead.experience or 'Not provided'}
**Referral Code:** {lead.referral_code or 'None'}
**Timestamp:** {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(lead.timestamp))}

---

### Action Required:
- [ ] Review lead
- [ ] Contact via {lead.contact.split('@')[0] if '@' in lead.contact else lead.contact}
- [ ] Send payment details
- [ ] Close when converted

**Labels:** lead, {lead.source}, {lead.plan_interest}
'''
        
        issue_data = {
            'title': title,
            'body': body,
            'labels': ['lead', lead.source, lead.plan_interest, 'needs-followup']
        }
        
        try:
            response = requests.post(
                f'https://api.github.com/repos/{self.repo}/issues',
                headers=self.headers,
                json=issue_data,
                timeout=10
            )
            if response.status_code == 201:
                issue_num = response.json()['number']
                print(f'Lead captured as issue #{issue_num}')
                return issue_num
            else:
                print(f'Error: {response.status_code} - {response.text}')
                return None
        except Exception as e:
            print(f'Error capturing lead: {e}')
            return None
    
    def capture_from_webhook(self, data: dict) -> Optional[int]:
        '''Capture lead from webhook (e.g., landing page form)'''
        lead = Lead(
            source=data.get('source', 'web'),
            contact=data.get('contact', ''),
            plan_interest=data.get('plan', 'founding'),
            experience=data.get('experience', ''),
            referral_code=data.get('ref', '')
        )
        return self.capture_lead(lead)


# Example usage
if __name__ == '__main__':
    # This would be called from webhook or CLI
    token = os.environ.get('MG_GH_TOKEN')
    if token:
        capture = LeadCapture(token)
        # capture.capture_lead(Lead(...))
        print('LeadCapture ready')
    else:
        print('Set MG_GH_TOKEN environment variable')