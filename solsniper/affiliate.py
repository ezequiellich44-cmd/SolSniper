#!/usr/bin/env python3
'''
SolSniper Affiliate/Referral Program

Built into the bot - users earn commissions for referring others.
'''

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Optional, Dict, List
from pathlib import Path


@dataclass
class Affiliate:
    '''Affiliate/referrer account'''
    code: str                    # Unique referral code
    wallet: str                  # Solana wallet for payouts
    created_at: float = field(default_factory=time.time)
    total_referrals: int = 0
    total_earnings: float = 0.0
    pending_earnings: float = 0.0
    referred_users: List[str] = field(default_factory=list)
    tier: str = 'bronze'         # bronze, silver, gold, platinum
    
    def to_dict(self) -> dict:
        return {
            'code': self.code,
            'wallet': self.wallet,
            'created_at': self.created_at,
            'total_referrals': self.total_referrals,
            'total_earnings': self.total_earnings,
            'pending_earnings': self.pending_earnings,
            'referred_users': self.referred_users,
            'tier': self.tier
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Affiliate':
        return cls(**data)


@dataclass
class Referral:
    '''A single referral'''
    referrer_code: str
    referred_user: str           # GitHub username or wallet
    plan_purchased: str          # 'founding', 'lifetime', 'monthly'
    amount_usd: float
    commission_usd: float
    status: str = 'pending'      # pending, confirmed, paid
    created_at: float = field(default_factory=time.time)
    paid_at: Optional[float] = None
    tx_signature: Optional[str] = None


class AffiliateProgram:
    '''
    Built-in affiliate program for SolSniper.
    
    Commission Structure:
    - Founding Member (.50):  commission (20%)
    - Pro Lifetime ():  commission (20%)
    - Pro Monthly (): /month recurring (20%)
    
    Tier Bonuses:
    - Bronze (0-4 refs): Base rate
    - Silver (5-19 refs): +5% bonus
    - Gold (20-49 refs): +10% bonus
    - Platinum (50+ refs): +15% bonus +  bonus
    '''
    
    COMMISSION_RATES = {
        'founding': 0.20,    # 20% of .50 = .90
        'lifetime': 0.20,    # 20% of  = .80
        'monthly': 0.20,     # 20% of  = .80/month
    }
    
    TIER_THRESHOLDS = {
        'bronze': (0, 0.00),
        'silver': (5, 0.05),
        'gold': (20, 0.10),
        'platinum': (50, 0.15),
    }
    
    TIER_BONUSES = {
        'platinum': 100.0,  #  bonus for reaching platinum
    }
    
    def __init__(self, storage_path: str = 'affiliates.json'):
        self.storage_path = Path(storage_path)
        self.affiliates: Dict[str, Affiliate] = {}
        self.referrals: List[Referral] = {}
        self._load()
    
    def _load(self):
        '''Load from storage'''
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.affiliates = {k: Affiliate.from_dict(v) for k, v in data.get('affiliates', {}).items()}
                    self.referrals = [Referral(**r) for r in data.get('referrals', [])]
            except Exception as e:
                print(f'Error loading affiliates: {e}')
    
    def _save(self):
        '''Save to storage'''
        data = {
            'affiliates': {k: v.to_dict() for k, v in self.affiliates.items()},
            'referrals': [r.__dict__ for r in self.referrals]
        }
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def generate_code(self, wallet: str) -> str:
        '''Generate unique referral code from wallet'''
        # Use first 8 chars of wallet hash
        hash_input = f'{wallet}{time.time()}'
        code = hashlib.sha256(hash_input.encode()).hexdigest()[:8].upper()
        return f'SOL{code}'
    
    def register_affiliate(self, wallet: str) -> Affiliate:
        '''Register new affiliate'''
        code = self.generate_code(wallet)
        
        # Check if wallet already registered
        for aff in self.affiliates.values():
            if aff.wallet == wallet:
                return aff
        
        affiliate = Affiliate(code=code, wallet=wallet)
        self.affiliates[code] = affiliate
        self._save()
        return affiliate
    
    def get_affiliate(self, code: str) -> Optional[Affiliate]:
        '''Get affiliate by code'''
        return self.affiliates.get(code.upper())
    
    def process_referral(self, referrer_code: str, referred_user: str, plan: str, tx_signature: str) -> Referral:
        '''Process a new referral'''
        referrer_code = referrer_code.upper()
        affiliate = self.affiliates.get(referrer_code)
        
        if not affiliate:
            raise ValueError(f'Invalid referral code: {referrer_code}')
        
        # Calculate commission
        base_rate = self.COMMISSION_RATES.get(plan, 0)
        tier_bonus = self.TIER_THRESHOLDS.get(affiliate.tier, (0, 0))[1]
        total_rate = base_rate + tier_bonus
        
        plan_prices = {'founding': 74.50, 'lifetime': 249.00, 'monthly': 49.00}
        amount = plan_prices.get(plan, 0)
        commission = amount * total_rate
        
        # Add platinum bonus if reaching threshold
        if affiliate.tier == 'platinum' and affiliate.total_referrals == 50:
            commission += self.TIER_BONUSES['platinum']
        
        referral = Referral(
            referrer_code=referrer_code,
            referred_user=referred_user,
            plan_purchased=plan,
            amount_usd=amount,
            commission_usd=round(commission, 2),
            tx_signature=tx_signature
        )
        
        self.referrals.append(referral)
        
        # Update affiliate stats
        affiliate.total_referrals += 1
        affiliate.pending_earnings += commission
        affiliate.referred_users.append(referred_user)
        
        # Update tier
        self._update_tier(affiliate)
        
        self._save()
        return referral
    
    def _update_tier(self, affiliate: Affiliate):
        '''Update affiliate tier based on referrals'''
        old_tier = affiliate.tier
        for tier, (threshold, bonus) in reversed(list(self.TIER_THRESHOLDS.items())):
            if affiliate.total_referrals >= threshold:
                affiliate.tier = tier
                break
        
        # Platinum bonus
        if affiliate.tier == 'platinum' and old_tier != 'platinum' and affiliate.total_referrals >= 50:
            affiliate.pending_earnings += self.TIER_BONUSES['platinum']
    
    def confirm_payment(self, tx_signature: str) -> bool:
        '''Confirm referral payment and move to earnings'''
        for referral in self.referrals:
            if referral.tx_signature == tx_signature and referral.status == 'pending':
                referral.status = 'confirmed'
                referral.paid_at = time.time()
                
                # Move to affiliate earnings
                affiliate = self.affiliates.get(referral.referrer_code)
                if affiliate:
                    affiliate.pending_earnings -= referral.commission_usd
                    affiliate.total_earnings += referral.commission_usd
                
                self._save()
                return True
        return False
    
    def get_stats(self, code: str) -> Optional[dict]:
        '''Get affiliate stats'''
        affiliate = self.affiliates.get(code.upper())
        if not affiliate:
            return None
        
        referrals = [r for r in self.referrals if r.referrer_code == code.upper()]
        
        return {
            'code': affiliate.code,
            'wallet': affiliate.wallet,
            'tier': affiliate.tier,
            'total_referrals': affiliate.total_referrals,
            'total_earnings': affiliate.total_earnings,
            'pending_earnings': affiliate.pending_earnings,
            'referred_users': affiliate.referred_users,
            'recent_referrals': [
                {
                    'user': r.referred_user,
                    'plan': r.plan_purchased,
                    'commission': r.commission_usd,
                    'status': r.status,
                    'date': r.created_at
                }
                for r in referrals[-10:]
            ]
        }
    
    def generate_referral_link(self, code: str) -> str:
        '''Generate referral link'''
        return f'https://github.com/ezequiellich44-cmd/SolSniper/issues/new?template=access_request.yml&ref={code}'


# CLI for testing
if __name__ == '__main__':
    program = AffiliateProgram()
    
    # Register test affiliate
    aff = program.register_affiliate('3fZSMAyCEMhZwWiynbJDjoYNUT97aiV9BLzoUNroEMAz')
    print(f'Affiliate: {aff.code}')
    print(f'Link: {program.generate_referral_link(aff.code)}')
    
    # Simulate referral
    ref = program.process_referral(aff.code, 'user123', 'founding', 'tx123')
    print(f'Referral: {ref.commission_usd} USD')
    
    stats = program.get_stats(aff.code)
    print(f'Stats: {stats}')