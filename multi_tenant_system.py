"""
MULTI-TENANT ARCHITECTURE
=========================
Enterprise multi-tenant system with workspace isolation,
team collaboration, role-based access control, and usage metering.

Features:
- Complete workspace isolation
- Team management and collaboration
- Granular role-based permissions
- Usage metering per tenant
- Tenant-specific configuration
- Data isolation and security
"""

import logging
import time
import json
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
from models import Base, get_session
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, ForeignKey, Index
from sqlalchemy.orm import relationship

logger = logging.getLogger(__name__)


class Role(str, Enum):
    """User roles in workspace."""
    OWNER = 'owner'
    ADMIN = 'admin'
    MEMBER = 'member'
    VIEWER = 'viewer'
    BILLING = 'billing'


class Permission(str, Enum):
    """Granular permissions."""
    # Workspace permissions
    WORKSPACE_DELETE = 'workspace:delete'
    WORKSPACE_SETTINGS = 'workspace:settings'
    WORKSPACE_BILLING = 'workspace:billing'
    
    # Team permissions
    TEAM_INVITE = 'team:invite'
    TEAM_REMOVE = 'team:remove'
    TEAM_MANAGE = 'team:manage'
    
    # Data permissions
    DATA_READ = 'data:read'
    DATA_WRITE = 'data:write'
    DATA_DELETE = 'data:delete'
    DATA_EXPORT = 'data:export'
    
    # Feature permissions
    FEATURES_AI = 'features:ai'
    FEATURES_ANALYTICS = 'features:analytics'
    FEATURES_AUTOMATION = 'features:automation'
    FEATURES_ADVANCED = 'features:advanced'


# Role permission mappings
ROLE_PERMISSIONS = {
    Role.OWNER: set(Permission),  # All permissions
    Role.ADMIN: {
        Permission.WORKSPACE_SETTINGS,
        Permission.TEAM_INVITE,
        Permission.TEAM_MANAGE,
        Permission.DATA_READ,
        Permission.DATA_WRITE,
        Permission.DATA_DELETE,
        Permission.DATA_EXPORT,
        Permission.FEATURES_AI,
        Permission.FEATURES_ANALYTICS,
        Permission.FEATURES_AUTOMATION,
        Permission.FEATURES_ADVANCED
    },
    Role.MEMBER: {
        Permission.DATA_READ,
        Permission.DATA_WRITE,
        Permission.DATA_EXPORT,
        Permission.FEATURES_AI,
        Permission.FEATURES_ANALYTICS,
        Permission.FEATURES_AUTOMATION
    },
    Role.VIEWER: {
        Permission.DATA_READ,
        Permission.FEATURES_ANALYTICS
    },
    Role.BILLING: {
        Permission.WORKSPACE_BILLING,
        Permission.DATA_READ
    }
}


# ---------------------------------------------------------------------------
# Database Models
# ---------------------------------------------------------------------------

class Workspace(Base):
    """Multi-tenant workspace."""
    __tablename__ = 'workspaces'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    owner_id = Column(String, index=True, nullable=False)
    
    # Plan and billing
    plan = Column(String, default='free')  # free, pro, enterprise
    status = Column(String, default='active')  # active, suspended, deleted
    
    # Usage limits
    max_team_members = Column(Integer, default=5)
    max_api_calls = Column(Integer, default=1000)
    max_storage_mb = Column(Integer, default=100)
    
    # Configuration (JSON)
    settings = Column(Text)  # JSON string
    
    # Timestamps
    created_at = Column(Float, default=time.time)
    updated_at = Column(Float, default=time.time)
    
    # Relationships
    members = relationship('WorkspaceMember', back_populates='workspace', cascade='all, delete-orphan')
    usage_records = relationship('WorkspaceUsage', back_populates='workspace', cascade='all, delete-orphan')
    
    # Indexes
    __table_args__ = (
        Index('idx_workspace_owner', owner_id),
        Index('idx_workspace_status', status),
    )


class WorkspaceMember(Base):
    """Workspace team member."""
    __tablename__ = 'workspace_members'
    
    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey('workspaces.id'), nullable=False)
    user_id = Column(String, index=True, nullable=False)
    
    # Role and permissions
    role = Column(String, default='member')
    custom_permissions = Column(Text)  # JSON array of additional permissions
    
    # Status
    status = Column(String, default='active')  # active, suspended, removed
    invited_by = Column(String)
    
    # Timestamps
    joined_at = Column(Float, default=time.time)
    last_active = Column(Float, default=time.time)
    
    # Relationships
    workspace = relationship('Workspace', back_populates='members')
    
    # Indexes
    __table_args__ = (
        Index('idx_member_workspace', workspace_id),
        Index('idx_member_user', user_id),
    )


class WorkspaceUsage(Base):
    """Usage tracking per workspace."""
    __tablename__ = 'workspace_usage'
    
    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey('workspaces.id'), nullable=False)
    
    # Usage counters (reset monthly)
    api_calls = Column(Integer, default=0)
    storage_mb = Column(Float, default=0)
    ai_requests = Column(Integer, default=0)
    export_count = Column(Integer, default=0)
    
    # Period
    period_start = Column(Float)
    period_end = Column(Float)
    
    # Relationships
    workspace = relationship('Workspace', back_populates='usage_records')
    
    # Indexes
    __table_args__ = (
        Index('idx_usage_workspace', workspace_id),
        Index('idx_usage_period', period_start, period_end),
    )


# ---------------------------------------------------------------------------
# Multi-Tenant Manager
# ---------------------------------------------------------------------------

class MultiTenantManager:
    """Manage multi-tenant operations."""
    
    def __init__(self):
        self.session = get_session()
    
    def create_workspace(
        self, 
        name: str, 
        owner_id: str, 
        plan: str = 'free',
        slug: Optional[str] = None
    ) -> Dict:
        """Create new workspace."""
        try:
            # Generate slug if not provided
            if not slug:
                slug = self._generate_slug(name)
            
            # Check if slug already exists
            existing = self.session.query(Workspace).filter_by(slug=slug).first()
            if existing:
                return {'success': False, 'error': 'Slug already exists'}
            
            # Create workspace
            workspace = Workspace(
                id=f'ws_{int(time.time())}_{owner_id[:8]}',
                name=name,
                slug=slug,
                owner_id=owner_id,
                plan=plan,
                status='active',
                settings=json.dumps({
                    'features': {'ai': True, 'analytics': True},
                    'notifications': {'email': True}
                })
            )
            
            # Set limits based on plan
            limits = self._get_plan_limits(plan)
            workspace.max_team_members = limits['team_members']
            workspace.max_api_calls = limits['api_calls']
            workspace.max_storage_mb = limits['storage_mb']
            
            self.session.add(workspace)
            
            # Add owner as member
            owner_member = WorkspaceMember(
                id=f'wm_{int(time.time())}_{owner_id[:8]}',
                workspace_id=workspace.id,
                user_id=owner_id,
                role=Role.OWNER.value,
                status='active'
            )
            
            self.session.add(owner_member)
            
            # Create initial usage record
            usage = WorkspaceUsage(
                id=f'wu_{int(time.time())}',
                workspace_id=workspace.id,
                period_start=time.time(),
                period_end=self._get_period_end()
            )
            self.session.add(usage)
            
            self.session.commit()
            
            logger.info(f"Created workspace: {workspace.id} ({slug})")
            
            return {
                'success': True,
                'workspace': {
                    'id': workspace.id,
                    'name': workspace.name,
                    'slug': workspace.slug,
                    'plan': workspace.plan,
                    'owner_id': workspace.owner_id
                }
            }
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to create workspace: {e}")
            return {'success': False, 'error': str(e)}
    
    def _generate_slug(self, name: str) -> str:
        """Generate URL-safe slug from name."""
        import re
        slug = name.lower()
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        slug = slug.strip('-')
        return slug[:50]
    
    def _get_plan_limits(self, plan: str) -> Dict:
        """Get usage limits for plan."""
        limits = {
            'free': {
                'team_members': 3,
                'api_calls': 1000,
                'storage_mb': 100
            },
            'pro': {
                'team_members': 10,
                'api_calls': 50000,
                'storage_mb': 5000
            },
            'enterprise': {
                'team_members': 100,
                'api_calls': 1000000,
                'storage_mb': 100000
            }
        }
        return limits.get(plan, limits['free'])
    
    def _get_period_end(self) -> float:
        """Get end of current billing period (30 days)."""
        from datetime import datetime, timedelta
        now = datetime.now()
        period_end = now + timedelta(days=30)
        return period_end.timestamp()
    
    def invite_member(
        self,
        workspace_id: str,
        inviter_id: str,
        user_id: str,
        role: str = 'member'
    ) -> Dict:
        """Invite user to workspace."""
        try:
            # Check if inviter has permission
            if not self.check_permission(workspace_id, inviter_id, Permission.TEAM_INVITE):
                return {'success': False, 'error': 'No permission to invite'}
            
            # Check if workspace exists
            workspace = self.session.query(Workspace).filter_by(id=workspace_id).first()
            if not workspace:
                return {'success': False, 'error': 'Workspace not found'}
            
            # Check team size limit
            current_members = self.session.query(WorkspaceMember).filter_by(
                workspace_id=workspace_id,
                status='active'
            ).count()
            
            if current_members >= workspace.max_team_members:
                return {'success': False, 'error': 'Team size limit reached'}
            
            # Check if user already member
            existing = self.session.query(WorkspaceMember).filter_by(
                workspace_id=workspace_id,
                user_id=user_id
            ).first()
            
            if existing:
                return {'success': False, 'error': 'User already a member'}
            
            # Create member
            member = WorkspaceMember(
                id=f'wm_{int(time.time())}_{user_id[:8]}',
                workspace_id=workspace_id,
                user_id=user_id,
                role=role,
                status='active',
                invited_by=inviter_id
            )
            
            self.session.add(member)
            self.session.commit()
            
            logger.info(f"Added member {user_id} to workspace {workspace_id}")
            
            return {
                'success': True,
                'member': {
                    'id': member.id,
                    'user_id': member.user_id,
                    'role': member.role,
                    'joined_at': member.joined_at
                }
            }
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to invite member: {e}")
            return {'success': False, 'error': str(e)}
    
    def remove_member(
        self,
        workspace_id: str,
        remover_id: str,
        user_id: str
    ) -> Dict:
        """Remove user from workspace."""
        try:
            # Check permission
            if not self.check_permission(workspace_id, remover_id, Permission.TEAM_REMOVE):
                return {'success': False, 'error': 'No permission to remove members'}
            
            # Cannot remove owner
            workspace = self.session.query(Workspace).filter_by(id=workspace_id).first()
            if workspace and workspace.owner_id == user_id:
                return {'success': False, 'error': 'Cannot remove workspace owner'}
            
            # Find member
            member = self.session.query(WorkspaceMember).filter_by(
                workspace_id=workspace_id,
                user_id=user_id
            ).first()
            
            if not member:
                return {'success': False, 'error': 'Member not found'}
            
            # Mark as removed
            member.status = 'removed'
            self.session.commit()
            
            logger.info(f"Removed member {user_id} from workspace {workspace_id}")
            
            return {'success': True}
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to remove member: {e}")
            return {'success': False, 'error': str(e)}
    
    def check_permission(
        self,
        workspace_id: str,
        user_id: str,
        permission: Permission
    ) -> bool:
        """Check if user has permission in workspace."""
        try:
            # Get member
            member = self.session.query(WorkspaceMember).filter_by(
                workspace_id=workspace_id,
                user_id=user_id,
                status='active'
            ).first()
            
            if not member:
                return False
            
            # Get role permissions
            role = Role(member.role)
            role_perms = ROLE_PERMISSIONS.get(role, set())
            
            # Check if permission granted
            if permission in role_perms:
                return True
            
            # Check custom permissions
            if member.custom_permissions:
                try:
                    custom = json.loads(member.custom_permissions)
                    if permission.value in custom:
                        return True
                except Exception:
                    pass
            
            return False
            
        except Exception as e:
            logger.error(f"Permission check failed: {e}")
            return False
    
    def track_usage(
        self,
        workspace_id: str,
        metric: str,
        amount: float = 1
    ) -> Dict:
        """Track usage for workspace."""
        try:
            # Get current usage record
            now = time.time()
            usage = self.session.query(WorkspaceUsage).filter(
                WorkspaceUsage.workspace_id == workspace_id,
                WorkspaceUsage.period_start <= now,
                WorkspaceUsage.period_end >= now
            ).first()
            
            if not usage:
                # Create new period
                usage = WorkspaceUsage(
                    id=f'wu_{int(time.time())}',
                    workspace_id=workspace_id,
                    period_start=now,
                    period_end=self._get_period_end()
                )
                self.session.add(usage)
            
            # Update metric
            if metric == 'api_calls':
                usage.api_calls += int(amount)
            elif metric == 'storage_mb':
                usage.storage_mb += amount
            elif metric == 'ai_requests':
                usage.ai_requests += int(amount)
            elif metric == 'export_count':
                usage.export_count += int(amount)
            
            self.session.commit()
            
            # Check if over limit
            workspace = self.session.query(Workspace).filter_by(id=workspace_id).first()
            if workspace:
                limits = {
                    'api_calls': workspace.max_api_calls,
                    'storage_mb': workspace.max_storage_mb
                }
                
                if metric in limits:
                    current = getattr(usage, metric, 0)
                    limit = limits[metric]
                    
                    if current >= limit:
                        return {
                            'success': True,
                            'over_limit': True,
                            'current': current,
                            'limit': limit
                        }
            
            return {'success': True, 'over_limit': False}
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Usage tracking failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_workspace_info(self, workspace_id: str) -> Optional[Dict]:
        """Get workspace information."""
        try:
            workspace = self.session.query(Workspace).filter_by(id=workspace_id).first()
            if not workspace:
                return None
            
            # Get member count
            member_count = self.session.query(WorkspaceMember).filter_by(
                workspace_id=workspace_id,
                status='active'
            ).count()
            
            # Get current usage
            now = time.time()
            usage = self.session.query(WorkspaceUsage).filter(
                WorkspaceUsage.workspace_id == workspace_id,
                WorkspaceUsage.period_start <= now,
                WorkspaceUsage.period_end >= now
            ).first()
            
            usage_data = {
                'api_calls': 0,
                'storage_mb': 0,
                'ai_requests': 0,
                'export_count': 0
            }
            
            if usage:
                usage_data = {
                    'api_calls': usage.api_calls,
                    'storage_mb': usage.storage_mb,
                    'ai_requests': usage.ai_requests,
                    'export_count': usage.export_count
                }
            
            return {
                'id': workspace.id,
                'name': workspace.name,
                'slug': workspace.slug,
                'owner_id': workspace.owner_id,
                'plan': workspace.plan,
                'status': workspace.status,
                'member_count': member_count,
                'limits': {
                    'team_members': workspace.max_team_members,
                    'api_calls': workspace.max_api_calls,
                    'storage_mb': workspace.max_storage_mb
                },
                'usage': usage_data,
                'created_at': workspace.created_at
            }
            
        except Exception as e:
            logger.error(f"Failed to get workspace info: {e}")
            return None
    
    def get_user_workspaces(self, user_id: str) -> List[Dict]:
        """Get all workspaces user belongs to."""
        try:
            members = self.session.query(WorkspaceMember).filter_by(
                user_id=user_id,
                status='active'
            ).all()
            
            workspaces = []
            for member in members:
                workspace = self.session.query(Workspace).filter_by(
                    id=member.workspace_id
                ).first()
                
                if workspace:
                    workspaces.append({
                        'id': workspace.id,
                        'name': workspace.name,
                        'slug': workspace.slug,
                        'role': member.role,
                        'plan': workspace.plan,
                        'joined_at': member.joined_at
                    })
            
            return workspaces
            
        except Exception as e:
            logger.error(f"Failed to get user workspaces: {e}")
            return []


# ---------------------------------------------------------------------------
# API Functions
# ---------------------------------------------------------------------------

def create_workspace_api(name: str, owner_id: str, plan: str = 'free') -> Dict:
    """Create new workspace."""
    manager = MultiTenantManager()
    return manager.create_workspace(name, owner_id, plan)


def invite_team_member(workspace_id: str, inviter_id: str, user_id: str, role: str = 'member') -> Dict:
    """Invite user to workspace team."""
    manager = MultiTenantManager()
    return manager.invite_member(workspace_id, inviter_id, user_id, role)


def remove_team_member(workspace_id: str, remover_id: str, user_id: str) -> Dict:
    """Remove user from workspace team."""
    manager = MultiTenantManager()
    return manager.remove_member(workspace_id, remover_id, user_id)


def check_user_permission(workspace_id: str, user_id: str, permission: str) -> bool:
    """Check if user has permission."""
    manager = MultiTenantManager()
    try:
        perm = Permission(permission)
        return manager.check_permission(workspace_id, user_id, perm)
    except ValueError:
        return False


def track_workspace_usage(workspace_id: str, metric: str, amount: float = 1) -> Dict:
    """Track usage metric for workspace."""
    manager = MultiTenantManager()
    return manager.track_usage(workspace_id, metric, amount)


def get_workspace_details(workspace_id: str) -> Optional[Dict]:
    """Get workspace details."""
    manager = MultiTenantManager()
    return manager.get_workspace_info(workspace_id)


def get_user_workspaces_api(user_id: str) -> Dict:
    """Get all workspaces for user."""
    manager = MultiTenantManager()
    workspaces = manager.get_user_workspaces(user_id)
    return {'workspaces': workspaces, 'count': len(workspaces)}
