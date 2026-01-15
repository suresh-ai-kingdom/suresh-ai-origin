"""
GLOBAL RIGHTS MANAGER
===========================
Manages permissions, rights, and authorization for global operations
Suresh AI Origin's permission and governance system
"""

import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field, asdict


class RightType(Enum):
    """Types of rights that can be granted"""
    READ = "read"
    WRITE = "write"
    DEPLOY = "deploy"
    AUTO_DEPLOY = "auto_deploy"
    MANAGE_USERS = "manage_users"
    MANAGE_BILLING = "manage_billing"
    ACCESS_ANALYTICS = "access_analytics"
    API_ACCESS = "api_access"
    WEBHOOK_DEPLOY = "webhook_deploy"
    INFRASTRUCTURE_CONTROL = "infrastructure_control"
    DOMAIN_MANAGEMENT = "domain_management"
    DNS_MANAGEMENT = "dns_management"
    CERTIFICATE_MANAGEMENT = "cert_management"
    AUTO_SCALING = "auto_scaling"
    AUTO_UPGRADE = "auto_upgrade"
    FINANCIAL_OPERATIONS = "financial_ops"
    STRATEGIC_DECISIONS = "decisions"
    PARTNER_AGREEMENTS = "partner_agreements"
    REVENUE_SHARE = "revenue_share"


class RightGrantor(Enum):
    """Who can grant rights"""
    SYSTEM = "system"
    ADMIN = "admin"
    BOARD = "board"
    LEGAL = "legal"
    PARTNER = "partner"


@dataclass
class AccessRight:
    """Individual access right"""
    right_id: str
    entity_id: str                   # User, service, or partner ID
    entity_type: str                 # "user", "service", "partner", "organization"
    entity_name: str
    right_type: RightType
    access_level: int                # 1-10 (1=minimal, 10=full)
    scope: str                       # "global", "regional", "service_specific"
    services: Set[str] = field(default_factory=set)  # Which services (empty = all)
    regions: Set[str] = field(default_factory=set)   # Which regions (empty = all)
    granted_at: float = field(default_factory=time.time)
    granted_by: str = "system"
    granted_by_role: RightGrantor = RightGrantor.SYSTEM
    expires_at: Optional[float] = None
    auto_renew: bool = False
    conditions: Dict = field(default_factory=dict)  # Rate limits, approval requirements, etc.
    
    def is_valid(self) -> bool:
        """Check if right is still valid"""
        if self.expires_at and time.time() > self.expires_at:
            return False
        return True
    
    def to_dict(self):
        data = asdict(self)
        data['right_type'] = self.right_type.value
        data['granted_by_role'] = self.granted_by_role.value
        data['services'] = list(self.services)
        data['regions'] = list(self.regions)
        return data


@dataclass
class RoleDefinition:
    """Pre-defined roles with standard rights"""
    role_id: str
    role_name: str
    description: str
    rights: List[RightType]
    access_levels: Dict[RightType, int]  # Default access level per right
    can_manage_users: bool = False
    max_api_calls_per_minute: int = 1000
    max_deployments_per_day: int = 100
    requires_approval: List[RightType] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)


class GlobalRightsManager:
    """
    Master rights management system for Suresh AI Origin
    Controls all permissions for global operations
    """
    
    def __init__(self):
        self.access_rights: Dict[str, AccessRight] = {}
        self.role_definitions: Dict[str, RoleDefinition] = {}
        self.approvals_queue: List[Dict] = []
        self.audit_log: List[Dict] = []
        self.delegations: Dict[str, List[str]] = {}  # user -> delegated_rights
        self.partnerships: Dict[str, Dict] = {}  # partner_id -> agreement
        self.api_keys: Dict[str, Dict] = {}  # api_key -> metadata
        
        self._initialize_default_roles()
    
    def _initialize_default_roles(self):
        """Initialize standard roles"""
        
        # Admin role - full access
        self.create_role_definition("admin", "Administrator", "Full system access",
            rights=[rt for rt in RightType],
            access_levels={rt: 10 for rt in RightType})
        
        # Operator role - manage operations
        self.create_role_definition("operator", "Operator", "Manage daily operations",
            rights=[RightType.DEPLOY, RightType.AUTO_DEPLOY, RightType.API_ACCESS,
                   RightType.AUTO_SCALING, RightType.AUTO_UPGRADE, RightType.ACCESS_ANALYTICS],
            access_levels={
                RightType.DEPLOY: 9,
                RightType.AUTO_DEPLOY: 9,
                RightType.API_ACCESS: 10,
                RightType.AUTO_SCALING: 9,
                RightType.AUTO_UPGRADE: 8,
                RightType.ACCESS_ANALYTICS: 10
            })
        
        # Finance role - billing and revenue
        self.create_role_definition("finance", "Finance", "Manage billing and revenue",
            rights=[RightType.MANAGE_BILLING, RightType.FINANCIAL_OPERATIONS,
                   RightType.REVENUE_SHARE, RightType.ACCESS_ANALYTICS],
            access_levels={
                RightType.MANAGE_BILLING: 10,
                RightType.FINANCIAL_OPERATIONS: 10,
                RightType.REVENUE_SHARE: 10,
                RightType.ACCESS_ANALYTICS: 9
            })
        
        # Developer role - API access
        self.create_role_definition("developer", "Developer", "API and integration access",
            rights=[RightType.API_ACCESS, RightType.READ, RightType.WRITE,
                   RightType.WEBHOOK_DEPLOY, RightType.ACCESS_ANALYTICS],
            access_levels={
                RightType.API_ACCESS: 10,
                RightType.READ: 10,
                RightType.WRITE: 8,
                RightType.WEBHOOK_DEPLOY: 7,
                RightType.ACCESS_ANALYTICS: 8
            })
        
        # Partner role - limited business access
        self.create_role_definition("partner", "Partner", "Partner ecosystem access",
            rights=[RightType.READ, RightType.API_ACCESS, RightType.REVENUE_SHARE,
                   RightType.PARTNER_AGREEMENTS, RightType.ACCESS_ANALYTICS],
            access_levels={
                RightType.READ: 10,
                RightType.API_ACCESS: 8,
                RightType.REVENUE_SHARE: 9,
                RightType.PARTNER_AGREEMENTS: 7,
                RightType.ACCESS_ANALYTICS: 7
            })
    
    def create_role_definition(self, role_id: str, role_name: str, description: str,
                              rights: List[RightType], 
                              access_levels: Dict[RightType, int]) -> RoleDefinition:
        """Create a new role definition"""
        role = RoleDefinition(
            role_id=role_id,
            role_name=role_name,
            description=description,
            rights=rights,
            access_levels=access_levels
        )
        self.role_definitions[role_id] = role
        self._audit_log(f"Created role: {role_name}", "role_created", {"role_id": role_id})
        return role
    
    def grant_right(self, entity_id: str, entity_type: str, entity_name: str,
                   right_type: RightType, access_level: int, scope: str,
                   services: Optional[Set[str]] = None,
                   regions: Optional[Set[str]] = None,
                   expires_in_days: Optional[int] = None,
                   conditions: Optional[Dict] = None) -> AccessRight:
        """
        Grant a specific right to an entity
        Can be auto-approved or require approval
        """
        right_id = f"right_{hashlib.md5(f'{entity_id}{right_type.value}{time.time()}'.encode()).hexdigest()[:12]}"
        
        expires_at = None
        if expires_in_days:
            expires_at = time.time() + (expires_in_days * 86400)
        
        right = AccessRight(
            right_id=right_id,
            entity_id=entity_id,
            entity_type=entity_type,
            entity_name=entity_name,
            right_type=right_type,
            access_level=access_level,
            scope=scope,
            services=services or set(),
            regions=regions or set(),
            expires_at=expires_at,
            conditions=conditions or {}
        )
        
        self.access_rights[right_id] = right
        
        self._audit_log(
            f"Granted {right_type.value} to {entity_name}",
            "right_granted",
            {
                "right_id": right_id,
                "entity_id": entity_id,
                "right_type": right_type.value,
                "access_level": access_level,
                "expires_at": expires_at
            }
        )
        
        return right
    
    def grant_role(self, entity_id: str, entity_type: str, entity_name: str,
                  role_id: str, expires_in_days: Optional[int] = None) -> List[AccessRight]:
        """
        Grant all rights associated with a role
        """
        role = self.role_definitions.get(role_id)
        if not role:
            return []
        
        granted_rights = []
        for right_type in role.rights:
            access_level = role.access_levels.get(right_type, 5)
            right = self.grant_right(
                entity_id, entity_type, entity_name,
                right_type, access_level, "global",
                expires_in_days=expires_in_days
            )
            granted_rights.append(right)
        
        self._audit_log(
            f"Assigned role {role_id} to {entity_name}",
            "role_assigned",
            {"entity_id": entity_id, "role_id": role_id, "rights_count": len(granted_rights)}
        )
        
        return granted_rights
    
    def can_perform_action(self, entity_id: str, right_type: RightType,
                         service_id: Optional[str] = None,
                         region: Optional[str] = None) -> Tuple[bool, str]:
        """
        Check if an entity can perform an action
        Returns (can_perform, reason)
        """
        # Find all rights for this entity
        entity_rights = [r for r in self.access_rights.values() 
                        if r.entity_id == entity_id and r.right_type == right_type]
        
        if not entity_rights:
            return False, f"No {right_type.value} right found"
        
        # Check validity
        valid_rights = [r for r in entity_rights if r.is_valid()]
        if not valid_rights:
            return False, f"{right_type.value} rights expired"
        
        # Check scope
        for right in valid_rights:
            scope_matches = True
            
            # Check service scope
            if right.services and service_id and service_id not in right.services:
                scope_matches = False
            
            # Check region scope
            if right.regions and region and region not in right.regions:
                scope_matches = False
            
            if scope_matches:
                return True, f"Authorized with access level {right.access_level}/10"
        
        return False, "Service or region not in scope"
    
    def delegate_right(self, from_entity: str, to_entity: str, right_id: str) -> bool:
        """
        Delegate a right to another entity
        """
        right = self.access_rights.get(right_id)
        if not right:
            return False
        
        if right.entity_id != from_entity:
            return False  # Can only delegate own rights
        
        if to_entity not in self.delegations:
            self.delegations[to_entity] = []
        
        self.delegations[to_entity].append(right_id)
        
        self._audit_log(
            f"Right delegated from {from_entity} to {to_entity}",
            "right_delegated",
            {"right_id": right_id, "from": from_entity, "to": to_entity}
        )
        
        return True
    
    def create_partnership_agreement(self, partner_id: str, partner_name: str,
                                   rights: List[RightType], revenue_share: float,
                                   term_months: int = 12) -> Dict:
        """
        Create partnership agreement with revenue sharing
        """
        agreement_id = f"agr_{hashlib.md5(f'{partner_id}{time.time()}'.encode()).hexdigest()[:12]}"
        
        agreement = {
            "agreement_id": agreement_id,
            "partner_id": partner_id,
            "partner_name": partner_name,
            "rights": [r.value for r in rights],
            "revenue_share": revenue_share,
            "created_at": time.time(),
            "expires_at": time.time() + (term_months * 30 * 86400),
            "term_months": term_months,
            "status": "active"
        }
        
        self.partnerships[partner_id] = agreement
        
        # Grant rights to partner
        for right_type in rights:
            self.grant_right(partner_id, "partner", partner_name, right_type, 8, "global")
        
        self._audit_log(
            f"Partnership created with {partner_name}",
            "partnership_created",
            {
                "agreement_id": agreement_id,
                "partner_id": partner_id,
                "revenue_share": revenue_share,
                "rights_count": len(rights)
            }
        )
        
        return agreement
    
    def generate_api_key(self, entity_id: str, entity_name: str,
                        rate_limit_per_min: int = 1000,
                        rate_limit_per_day: int = 100000) -> str:
        """
        Generate API key with rate limits
        """
        api_key = f"sk_{hashlib.sha256(f'{entity_id}{time.time()}'.encode()).hexdigest()[:32]}"
        
        self.api_keys[api_key] = {
            "entity_id": entity_id,
            "entity_name": entity_name,
            "created_at": time.time(),
            "rate_limit_per_min": rate_limit_per_min,
            "rate_limit_per_day": rate_limit_per_day,
            "calls_this_minute": 0,
            "calls_today": 0,
            "active": True
        }
        
        self._audit_log(
            f"API key generated for {entity_name}",
            "api_key_generated",
            {"entity_id": entity_id, "rate_limits": (rate_limit_per_min, rate_limit_per_day)}
        )
        
        return api_key
    
    def verify_api_key(self, api_key: str) -> Tuple[bool, str]:
        """Verify API key is valid and not rate limited"""
        key_data = self.api_keys.get(api_key)
        
        if not key_data:
            return False, "Invalid API key"
        
        if not key_data["active"]:
            return False, "API key disabled"
        
        if key_data["calls_this_minute"] >= key_data["rate_limit_per_min"]:
            return False, "Rate limit exceeded (per minute)"
        
        if key_data["calls_today"] >= key_data["rate_limit_per_day"]:
            return False, "Rate limit exceeded (per day)"
        
        return True, "Valid"
    
    def get_entity_rights(self, entity_id: str) -> List[AccessRight]:
        """Get all rights for an entity"""
        entity_rights = [r for r in self.access_rights.values() if r.entity_id == entity_id]
        # Add delegated rights
        if entity_id in self.delegations:
            for right_id in self.delegations[entity_id]:
                if right_id in self.access_rights:
                    entity_rights.append(self.access_rights[right_id])
        return entity_rights
    
    def revoke_right(self, right_id: str) -> bool:
        """Revoke a specific right"""
        if right_id in self.access_rights:
            right = self.access_rights[right_id]
            del self.access_rights[right_id]
            self._audit_log(
                f"Right revoked: {right.right_type.value}",
                "right_revoked",
                {"right_id": right_id, "entity_id": right.entity_id}
            )
            return True
        return False
    
    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """Get audit log"""
        return self.audit_log[-limit:]
    
    def _audit_log(self, message: str, event_type: str, details: Dict):
        """Internal audit logging"""
        self.audit_log.append({
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "message": message,
            "event_type": event_type,
            "details": details
        })
        if len(self.audit_log) > 10000:
            self.audit_log = self.audit_log[-10000:]
    
    def get_rights_summary(self) -> Dict:
        """Get summary of all rights in system"""
        return {
            "total_rights": len(self.access_rights),
            "active_rights": len([r for r in self.access_rights.values() if r.is_valid()]),
            "expired_rights": len([r for r in self.access_rights.values() if not r.is_valid()]),
            "role_definitions": len(self.role_definitions),
            "partnerships": len(self.partnerships),
            "api_keys_active": len([k for k in self.api_keys.values() if k["active"]]),
            "delegations": len(self.delegations)
        }


def demo_global_rights():
    """Demo of global rights management"""
    print("\n" + "="*80)
    print("🔐 GLOBAL RIGHTS MANAGER - PERMISSION & GOVERNANCE SYSTEM")
    print("="*80)
    
    manager = GlobalRightsManager()
    
    # Phase 1: Show default roles
    print("\n📋 PHASE 1: DEFAULT ROLES")
    print("-" * 80)
    for role_id, role in manager.role_definitions.items():
        print(f"✓ {role.role_name:15} | Rights: {len(role.rights):2} | Access Levels: {list(role.access_levels.values())[:3]}")
    
    # Phase 2: Grant rights
    print("\n🔓 PHASE 2: GRANTING RIGHTS TO OPERATORS")
    print("-" * 80)
    
    # Grant admin role to system
    admin_rights = manager.grant_role("sys_admin", "user", "System Admin", "admin", expires_in_days=365)
    print(f"✓ Granted 'admin' role (20 rights) to System Admin")
    
    # Grant operator role
    operator_rights = manager.grant_role("op_01", "user", "Operations Lead", "operator", expires_in_days=180)
    print(f"✓ Granted 'operator' role (6 rights) to Operations Lead")
    
    # Grant developer role
    dev_rights = manager.grant_role("dev_01", "user", "Senior Developer", "developer", expires_in_days=365)
    print(f"✓ Granted 'developer' role (5 rights) to Senior Developer")
    
    # Phase 3: Create partnerships
    print("\n🤝 PHASE 3: CREATING PARTNERSHIP AGREEMENTS")
    print("-" * 80)
    
    partner_agreement = manager.create_partnership_agreement(
        "partner_001",
        "TechVenture Partners",
        [RightType.API_ACCESS, RightType.REVENUE_SHARE, RightType.PARTNER_AGREEMENTS],
        revenue_share=25.0,
        term_months=24
    )
    print(f"✓ Partnership: TechVenture Partners | Revenue Share: 25% | Term: 24 months")
    print(f"  Agreement ID: {partner_agreement['agreement_id']}")
    
    # Phase 4: Generate API keys
    print("\n🔑 PHASE 4: GENERATING API KEYS")
    print("-" * 80)
    
    api_key_1 = manager.generate_api_key("dev_01", "Senior Developer", 5000, 500000)
    api_key_2 = manager.generate_api_key("partner_001", "TechVenture Partners", 2000, 200000)
    
    print(f"✓ API Key generated for Senior Developer")
    print(f"  Rate limit: 5,000 req/min | 500,000 req/day")
    print(f"✓ API Key generated for TechVenture Partners")
    print(f"  Rate limit: 2,000 req/min | 200,000 req/day")
    
    # Phase 5: Permission checks
    print("\n✅ PHASE 5: PERMISSION VERIFICATION")
    print("-" * 80)
    
    can_deploy, reason = manager.can_perform_action("op_01", RightType.AUTO_DEPLOY)
    print(f"✓ Operations Lead → AUTO_DEPLOY: {can_deploy} ({reason})")
    
    can_access, reason = manager.can_perform_action("partner_001", RightType.API_ACCESS)
    print(f"✓ TechVenture Partners → API_ACCESS: {can_access} ({reason})")
    
    can_bill, reason = manager.can_perform_action("dev_01", RightType.MANAGE_BILLING)
    print(f"✗ Senior Developer → MANAGE_BILLING: {can_bill} ({reason})")
    
    # Phase 6: Rights summary
    print("\n📊 PHASE 6: SYSTEM SUMMARY")
    print("-" * 80)
    
    summary = manager.get_rights_summary()
    print(f"Total Rights Granted: {summary['total_rights']}")
    print(f"Active Rights: {summary['active_rights']}")
    print(f"Role Definitions: {summary['role_definitions']}")
    print(f"Active Partnerships: {summary['partnerships']}")
    print(f"Active API Keys: {summary['api_keys_active']}")
    
    print("\n" + "="*80)
    print("✨ GLOBAL RIGHTS SYSTEM OPERATIONAL")
    print("   • 5 pre-defined roles (Admin, Operator, Finance, Developer, Partner)")
    print("   • Auto-deploy rights granted to trusted entities")
    print("   • Partnership agreements with revenue sharing")
    print("   • API keys with rate limiting")
    print("   • Full audit trail of all permissions")
    print("="*80 + "\n")


if __name__ == "__main__":
    demo_global_rights()
