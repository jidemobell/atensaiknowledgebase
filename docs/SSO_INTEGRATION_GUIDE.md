# 🔐 OpenWebUI SSO Integration Guide

## 🎯 Overview

This guide provides comprehensive instructions for integrating Single Sign-On (SSO) with your OpenWebUI Novel Knowledge Fusion Platform. While this guide covers general SSO principles and OpenWebUI configuration, it's designed to help you prepare for IBM SSO integration.

## 🏗️ SSO Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    SSO Flow Architecture                   │
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │ User Browser    │    │ IBM SSO/SAML    │                │
│  │ (Client)        │    │ Identity Provider│               │
│  └─────────┬───────┘    └─────────┬───────┘                │
│           │                       │                        │
│           │ 1. Login Request      │                        │
│           ├───────────────────────►                        │
│           │                       │                        │
│           │ 2. SAML Response      │                        │
│           ◄───────────────────────┤                        │
│           │                       │                        │
│           │ 3. Access Token       │                        │
│           │                       │                        │
│           ▼                       │                        │
│  ┌─────────────────┐              │                        │
│  │ OpenWebUI       │              │                        │
│  │ (Service Provider)              │                        │
│  │ - Authentication│              │                        │
│  │ - Authorization │              │                        │
│  │ - User Management              │                        │
│  └─────────────────┘              │                        │
│           │                       │                        │
│           │ 4. Validate Token     │                        │
│           ├───────────────────────►                        │
│           │                       │                        │
│           │ 5. User Info          │                        │
│           ◄───────────────────────┤                        │
│           │                       │                        │
│           ▼                       │                        │
│  ┌─────────────────┐              │                        │
│  │ Knowledge Fusion│              │                        │
│  │ Backend Services│              │                        │
│  │ - API Access    │              │                        │
│  │ - Role-based    │              │                        │
│  │   Authorization │              │                        │
│  └─────────────────┘              │                        │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 OpenWebUI SSO Configuration

### 1. Environment Variables Setup

Create or update your `.env` file with SSO configuration:

```bash
# SSO Configuration
ENABLE_OAUTH=true
OAUTH_CLIENT_ID=your_ibm_client_id
OAUTH_CLIENT_SECRET=your_ibm_client_secret
OAUTH_SCOPES=openid,profile,email
OAUTH_PROVIDER_NAME=IBM SSO

# SAML Configuration (if using SAML instead of OAuth)
ENABLE_SAML=true
SAML_ENTITY_ID=your_openwebui_entity_id
SAML_IDP_ENTITY_ID=your_ibm_idp_entity_id
SAML_IDP_URL=https://your-ibm-sso.com/saml/sso
SAML_IDP_SLO_URL=https://your-ibm-sso.com/saml/slo

# IBM-Specific Settings
IBM_SSO_DISCOVERY_URL=https://your-ibm-sso.com/.well-known/openid_configuration
IBM_SSO_ISSUER=https://your-ibm-sso.com
IBM_SSO_AUTHORIZATION_URL=https://your-ibm-sso.com/oauth2/authorize
IBM_SSO_TOKEN_URL=https://your-ibm-sso.com/oauth2/token
IBM_SSO_USERINFO_URL=https://your-ibm-sso.com/oauth2/userinfo

# User Management
SSO_AUTO_CREATE_USERS=true
SSO_UPDATE_USER_INFO=true
DEFAULT_USER_ROLE=user
ADMIN_EMAIL=admin@your-company.com

# Session Management
SESSION_SECRET=your_secure_session_secret
SESSION_TIMEOUT=28800  # 8 hours in seconds
ENABLE_SESSION_PERSISTENCE=true

# Security Settings
ENFORCE_DOMAIN_RESTRICTION=true
ALLOWED_EMAIL_DOMAINS=@your-company.com,@ibm.com
REQUIRE_EMAIL_VERIFICATION=false  # IBM SSO handles this
```

### 2. Docker Compose Configuration

Update your `docker-compose.yml` to include SSO environment variables:

```yaml
version: '3.8'

services:
  openwebui:
    build:
      context: .
      dockerfile: docker/Dockerfile.frontend
    container_name: openwebui-frontend
    ports:
      - "8080:8080"
    environment:
      - NODE_ENV=production
      - BACKEND_URL=http://knowledge-fusion:8003
      - OLLAMA_BASE_URL=http://ollama:11434
      
      # SSO Configuration
      - ENABLE_OAUTH=${ENABLE_OAUTH:-false}
      - OAUTH_CLIENT_ID=${OAUTH_CLIENT_ID}
      - OAUTH_CLIENT_SECRET=${OAUTH_CLIENT_SECRET}
      - OAUTH_SCOPES=${OAUTH_SCOPES:-openid,profile,email}
      - OAUTH_PROVIDER_NAME=${OAUTH_PROVIDER_NAME:-IBM SSO}
      
      # IBM SSO URLs
      - IBM_SSO_DISCOVERY_URL=${IBM_SSO_DISCOVERY_URL}
      - IBM_SSO_ISSUER=${IBM_SSO_ISSUER}
      - IBM_SSO_AUTHORIZATION_URL=${IBM_SSO_AUTHORIZATION_URL}
      - IBM_SSO_TOKEN_URL=${IBM_SSO_TOKEN_URL}
      - IBM_SSO_USERINFO_URL=${IBM_SSO_USERINFO_URL}
      
      # User Management
      - SSO_AUTO_CREATE_USERS=${SSO_AUTO_CREATE_USERS:-true}
      - SSO_UPDATE_USER_INFO=${SSO_UPDATE_USER_INFO:-true}
      - DEFAULT_USER_ROLE=${DEFAULT_USER_ROLE:-user}
      - ADMIN_EMAIL=${ADMIN_EMAIL}
      
      # Security
      - SESSION_SECRET=${SESSION_SECRET}
      - SESSION_TIMEOUT=${SESSION_TIMEOUT:-28800}
      - ENFORCE_DOMAIN_RESTRICTION=${ENFORCE_DOMAIN_RESTRICTION:-true}
      - ALLOWED_EMAIL_DOMAINS=${ALLOWED_EMAIL_DOMAINS}
      
    volumes:
      - webui_data:/app/data
    depends_on:
      - knowledge-fusion
      - ollama
    restart: unless-stopped

  # Add Redis for session storage (recommended for SSO)
  redis-sessions:
    image: redis:7-alpine
    container_name: redis-sessions
    ports:
      - "6380:6379"
    volumes:
      - redis_session_data:/data
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    restart: unless-stopped

volumes:
  webui_data:
  redis_session_data:
```

## 🔑 IBM SSO Integration Types

### Option 1: OAuth 2.0 / OpenID Connect (Recommended)

#### Configuration Steps:
1. **Register Application in IBM SSO**
   ```json
   {
     "application_name": "OpenWebUI Knowledge Fusion Platform",
     "application_type": "web",
     "redirect_uris": [
       "https://your-openwebui-domain.com/auth/oauth/callback",
       "http://localhost:8080/auth/oauth/callback"
     ],
     "scopes": ["openid", "profile", "email", "groups"],
     "grant_types": ["authorization_code"],
     "response_types": ["code"]
   }
   ```

2. **OpenWebUI OAuth Configuration**
   ```javascript
   // In OpenWebUI configuration
   const oauthConfig = {
     provider: 'ibm',
     clientId: process.env.OAUTH_CLIENT_ID,
     clientSecret: process.env.OAUTH_CLIENT_SECRET,
     discoveryUrl: process.env.IBM_SSO_DISCOVERY_URL,
     scope: 'openid profile email groups',
     
     // IBM-specific endpoints
     authorizationURL: process.env.IBM_SSO_AUTHORIZATION_URL,
     tokenURL: process.env.IBM_SSO_TOKEN_URL,
     userInfoURL: process.env.IBM_SSO_USERINFO_URL,
     
     // User mapping
     userMapping: {
       id: 'sub',
       email: 'email', 
       name: 'name',
       firstName: 'given_name',
       lastName: 'family_name',
       groups: 'groups'
     }
   };
   ```

### Option 2: SAML 2.0

#### Configuration Steps:
1. **SAML Service Provider Configuration**
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <EntityDescriptor entityID="https://your-openwebui-domain.com/saml/metadata"
                     xmlns="urn:oasis:names:tc:SAML:2.0:metadata">
     <SPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
       <NameIDFormat>urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress</NameIDFormat>
       <AssertionConsumerService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
                                Location="https://your-openwebui-domain.com/auth/saml/callback"
                                index="1" isDefault="true"/>
     </SPSSODescriptor>
   </EntityDescriptor>
   ```

2. **SAML Attribute Mapping**
   ```json
   {
     "attributeMapping": {
       "email": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
       "firstName": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname", 
       "lastName": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname",
       "groups": "http://schemas.microsoft.com/ws/2008/06/identity/claims/groups",
       "employeeId": "http://schemas.your-company.com/identity/claims/employeeid"
     }
   }
   ```

## 👥 User Management & Role Mapping

### 1. IBM Group to OpenWebUI Role Mapping

```javascript
// Role mapping configuration
const roleMapping = {
  // IBM SSO Groups -> OpenWebUI Roles
  'cn=openwebui-admins,ou=groups,dc=ibm,dc=com': 'admin',
  'cn=ai-researchers,ou=groups,dc=ibm,dc=com': 'user',
  'cn=knowledge-managers,ou=groups,dc=ibm,dc=com': 'manager',
  'cn=readonly-users,ou=groups,dc=ibm,dc=com': 'viewer',
  
  // Default role for users not in specific groups
  'default': 'user'
};

// Permission matrix
const permissions = {
  'admin': [
    'manage_users',
    'manage_models', 
    'access_all_conversations',
    'system_settings',
    'api_access',
    'export_data'
  ],
  'manager': [
    'manage_team_conversations',
    'access_analytics',
    'model_selection',
    'api_access'
  ],
  'user': [
    'create_conversations',
    'access_own_conversations',
    'use_models',
    'basic_api_access'
  ],
  'viewer': [
    'view_conversations',
    'read_only_access'
  ]
};
```

### 2. User Provisioning Configuration

```javascript
// Automatic user provisioning
const userProvisioning = {
  autoCreateUsers: true,
  updateUserInfo: true,
  
  // User attributes from IBM SSO
  userAttributes: {
    email: 'required',
    firstName: 'required', 
    lastName: 'required',
    employeeId: 'optional',
    department: 'optional',
    manager: 'optional',
    location: 'optional'
  },
  
  // Default settings for new users
  defaultSettings: {
    language: 'en',
    theme: 'dark',
    notifications: true,
    analyticsOptIn: false
  }
};
```

## 🔒 Security Configuration

### 1. Security Headers & Policies

```nginx
# Nginx configuration for SSO security
server {
    listen 443 ssl http2;
    server_name your-openwebui-domain.com;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
    
    # SSO-specific headers
    add_header X-SSO-Provider "IBM" always;
    
    location /auth/ {
        proxy_pass http://openwebui:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # SSO session headers
        proxy_set_header X-SSO-Session $cookie_sso_session;
        proxy_set_header X-User-Groups $http_x_user_groups;
    }
}
```

### 2. Session Management

```javascript
// Session configuration
const sessionConfig = {
  store: 'redis', // Use Redis for distributed sessions
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  
  cookie: {
    secure: true, // HTTPS only in production
    httpOnly: true,
    maxAge: 8 * 60 * 60 * 1000, // 8 hours
    sameSite: 'strict'
  },
  
  // IBM SSO session sync
  ssoSync: {
    enabled: true,
    validateInterval: 15 * 60 * 1000, // 15 minutes
    refreshThreshold: 30 * 60 * 1000, // 30 minutes before expiry
    logoutUrl: 'https://your-ibm-sso.com/logout'
  }
};
```

## 🚀 Implementation Steps

### Phase 1: Preparation (Week 1)
1. **Requirements Gathering**
   - [ ] Identify IBM SSO endpoints and configuration
   - [ ] Determine user attributes available from IBM SSO
   - [ ] Define role mapping requirements
   - [ ] Plan user migration strategy

2. **Environment Setup**
   - [ ] Set up development environment with SSO simulation
   - [ ] Configure test IBM SSO application
   - [ ] Update OpenWebUI configuration files
   - [ ] Test basic authentication flow

### Phase 2: Core Implementation (Week 2)
1. **Authentication Integration**
   - [ ] Implement OAuth 2.0/OIDC flow
   - [ ] Configure SAML if required
   - [ ] Set up token validation
   - [ ] Implement logout handling

2. **User Management**
   - [ ] Configure automatic user provisioning
   - [ ] Implement role mapping
   - [ ] Set up group synchronization
   - [ ] Test user attribute mapping

### Phase 3: Security & Testing (Week 3)
1. **Security Hardening**
   - [ ] Configure session management
   - [ ] Implement security headers
   - [ ] Set up audit logging
   - [ ] Test security scenarios

2. **Integration Testing**
   - [ ] Test with IBM SSO staging environment
   - [ ] Validate user journeys
   - [ ] Performance testing
   - [ ] Security testing

### Phase 4: Production Deployment (Week 4)
1. **Production Configuration**
   - [ ] Configure production IBM SSO
   - [ ] Set up monitoring and alerting
   - [ ] Deploy to production environment
   - [ ] User acceptance testing

2. **Go-Live Activities**
   - [ ] User communication and training
   - [ ] Gradual rollout strategy
   - [ ] Monitor and resolve issues
   - [ ] Post-deployment validation

## 🔧 Configuration Files

### 1. OpenWebUI SSO Configuration

Create `config/sso.json`:
```json
{
  "sso": {
    "enabled": true,
    "provider": "ibm",
    "enforceSSO": true,
    "allowLocalAuth": false,
    
    "oauth": {
      "clientId": "${OAUTH_CLIENT_ID}",
      "clientSecret": "${OAUTH_CLIENT_SECRET}",
      "discoveryUrl": "${IBM_SSO_DISCOVERY_URL}",
      "scope": "openid profile email groups",
      "responseType": "code",
      "grantType": "authorization_code"
    },
    
    "userMapping": {
      "idAttribute": "sub",
      "emailAttribute": "email",
      "nameAttribute": "name",
      "firstNameAttribute": "given_name",
      "lastNameAttribute": "family_name",
      "groupsAttribute": "groups"
    },
    
    "roleMapping": {
      "adminGroups": ["openwebui-admins", "system-administrators"],
      "managerGroups": ["ai-team-leads", "knowledge-managers"],
      "userGroups": ["ai-researchers", "general-users"],
      "viewerGroups": ["readonly-users"],
      "defaultRole": "user"
    },
    
    "sessionManagement": {
      "timeout": 28800,
      "renewalThreshold": 1800,
      "logoutRedirect": "https://your-ibm-sso.com/logout"
    }
  }
}
```

### 2. Backend API Authentication

Update your Novel Knowledge Fusion backend for SSO:

```python
# In your enhanced_backend files
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import requests

class SSOAuthenticator:
    def __init__(self):
        self.ibm_sso_public_key_url = os.getenv('IBM_SSO_JWKS_URL')
        self.ibm_sso_issuer = os.getenv('IBM_SSO_ISSUER')
        
    async def validate_token(self, token: str):
        """Validate JWT token from IBM SSO"""
        try:
            # Get public keys from IBM SSO
            response = requests.get(self.ibm_sso_public_key_url)
            jwks = response.json()
            
            # Validate token
            decoded = jwt.decode(
                token, 
                jwks, 
                algorithms=['RS256'],
                issuer=self.ibm_sso_issuer,
                audience=os.getenv('OAUTH_CLIENT_ID')
            )
            
            return decoded
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    async def get_user_info(self, token_data: dict):
        """Extract user information from token"""
        return {
            'user_id': token_data.get('sub'),
            'email': token_data.get('email'),
            'name': token_data.get('name'),
            'groups': token_data.get('groups', []),
            'roles': self._map_groups_to_roles(token_data.get('groups', []))
        }
    
    def _map_groups_to_roles(self, groups: list):
        """Map IBM SSO groups to OpenWebUI roles"""
        role_mapping = {
            'openwebui-admins': 'admin',
            'ai-researchers': 'user',
            'knowledge-managers': 'manager'
        }
        
        roles = []
        for group in groups:
            if group in role_mapping:
                roles.append(role_mapping[group])
        
        return roles if roles else ['user']

# Use in your FastAPI endpoints
security = HTTPBearer()
sso_auth = SSOAuthenticator()

@app.post("/synthesize")
async def synthesize_knowledge(
    request: KnowledgeRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Validate SSO token
    token_data = await sso_auth.validate_token(credentials.credentials)
    user_info = await sso_auth.get_user_info(token_data)
    
    # Check permissions
    if 'admin' not in user_info['roles'] and 'user' not in user_info['roles']:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Your existing synthesis logic with user context
    return await perform_synthesis(request, user_context=user_info)
```

## 📊 Monitoring & Logging

### 1. SSO-Specific Monitoring

```javascript
// Monitoring configuration
const ssoMonitoring = {
  metrics: {
    'sso_login_attempts': 'counter',
    'sso_login_success': 'counter', 
    'sso_login_failures': 'counter',
    'sso_token_validation_time': 'histogram',
    'sso_session_duration': 'histogram',
    'active_sso_sessions': 'gauge'
  },
  
  alerts: {
    'high_login_failure_rate': {
      condition: 'sso_login_failures / sso_login_attempts > 0.1',
      action: 'notify_security_team'
    },
    'token_validation_slow': {
      condition: 'sso_token_validation_time > 5s',
      action: 'notify_ops_team'  
    }
  }
};
```

### 2. Audit Logging

```javascript
// Audit log structure
const auditLog = {
  timestamp: new Date().toISOString(),
  eventType: 'sso_login',
  userId: user.id,
  userEmail: user.email,
  sourceIP: request.ip,
  userAgent: request.headers['user-agent'],
  ssoProvider: 'ibm',
  sessionId: session.id,
  success: true,
  additionalData: {
    groups: user.groups,
    roles: user.roles,
    tokenIssuer: 'https://your-ibm-sso.com'
  }
};
```

## 🔍 Testing Strategies

### 1. Unit Tests
```javascript
// Example SSO unit tests
describe('SSO Authentication', () => {
  test('should validate IBM SSO token', async () => {
    const mockToken = generateMockIBMToken();
    const result = await ssoAuth.validateToken(mockToken);
    expect(result.email).toBe('test@ibm.com');
  });
  
  test('should map IBM groups to roles correctly', () => {
    const groups = ['openwebui-admins', 'ai-researchers'];
    const roles = ssoAuth.mapGroupsToRoles(groups);
    expect(roles).toContain('admin');
    expect(roles).toContain('user');
  });
});
```

### 2. Integration Tests
```bash
# Test SSO flow end-to-end
curl -X POST http://localhost:8080/auth/oauth/login \
  -H "Content-Type: application/json" \
  -d '{"provider": "ibm"}'

# Test protected endpoint with SSO token
curl -X POST http://localhost:8003/synthesize \
  -H "Authorization: Bearer ${IBM_SSO_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"query": "test with SSO authentication"}'
```

## ⚠️ Common Issues & Troubleshooting

### 1. Token Validation Issues
```bash
# Check IBM SSO connectivity
curl -v https://your-ibm-sso.com/.well-known/openid_configuration

# Validate token manually
curl -X POST https://your-ibm-sso.com/oauth2/introspect \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -d "token=${JWT_TOKEN}"
```

### 2. User Mapping Issues
```javascript
// Debug user attribute mapping
console.log('IBM SSO User Data:', ssoUserData);
console.log('Mapped User:', mappedUser);
console.log('Assigned Roles:', assignedRoles);
```

### 3. Session Issues
```bash
# Check Redis session storage
docker-compose exec redis-sessions redis-cli
> KEYS "sess:*"
> GET "sess:session_id_here"
```

## 📚 Additional Resources

### IBM SSO Documentation
- IBM Security Verify Documentation
- IBM Cloud Identity and Access Management
- SAML 2.0 Configuration Guides
- OAuth 2.0 / OpenID Connect Specifications

### OpenWebUI Integration
- OpenWebUI Authentication Documentation
- Custom Authentication Provider Development
- Session Management Best Practices
- Security Configuration Guidelines

## 🎯 Next Steps

1. **Review this guide** with your IBM SSO team
2. **Identify specific IBM SSO endpoints** and configuration requirements
3. **Plan pilot deployment** with a small group of users
4. **Implement monitoring and logging** for production readiness
5. **Test thoroughly** in staging environment before production rollout

---

*This guide provides the foundation for integrating IBM SSO with your Novel Knowledge Fusion Platform. Customize the configuration based on your specific IBM SSO setup and organizational requirements.*
