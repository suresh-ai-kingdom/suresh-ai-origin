# iOS SDK (Swift)

## Overview
Official Swift package for integrating SURESH AI ORIGIN with iOS apps.

## Installation

```swift
// Package.swift
.package(url: "https://github.com/suresh-ai-kingdom/suresh-ios-sdk.git", from: "1.0.0")

dependencies: [
    .product(name: "SureshAI", package: "suresh-ios-sdk")
]
```

## Quick Start

```swift
import SureshAI

// Initialize
let client = SureshAI.Client(
    apiKey: "your_jwt_token",
    environment: .production
)

// Authenticate
let session = try await client.auth.login(
    email: "user@example.com",
    password: "password"
)

// Save token
UserDefaults.standard.set(session.token, forKey: "suresh_token")

// Generate content
let content = try await client.content.generate(
    prompt: "Write a marketing email",
    tone: "professional"
)

print(content.text)
```

## Features

### Offline Support
```swift
// Sync queue for offline changes
let syncQueue = client.sync.queue()

// Add action while offline
syncQueue.add(
    action: .create,
    resource: .content,
    data: ["title": "My Content"]
)

// Auto-sync when online
try await syncQueue.sync()
```

### Caching
```swift
// Automatic caching
let prompts = try await client.content.prompts(
    cache: true,
    ttl: 3600  // 1 hour
)
```

### Analytics
```swift
// Track events
try await client.analytics.track(
    event: "content_generated",
    properties: ["prompt": "email", "tone": "professional"]
)

// Get usage stats
let stats = try await client.analytics.usage()
print("Credits remaining: \(stats.creditsRemaining)")
```

### Push Notifications
```swift
// Request push permission
let granted = try await client.push.requestPermission()

if granted {
    let deviceToken = /* get from APNs */
    try await client.push.register(deviceToken: deviceToken)
}

// Handle push
client.push.onNotification { notification in
    print("Received: \(notification.title)")
}
```

## Architecture

### Core Classes
- `Client` - Main entry point
- `AuthManager` - JWT + refresh tokens
- `ContentManager` - AI generation API
- `SyncManager` - Offline queue + conflict resolution
- `CacheManager` - CoreData backed cache
- `AnalyticsManager` - Event tracking
- `PushManager` - FCM device registration

### Storage (CoreData)
- `CachedContent` - Generated content
- `SyncQueue` - Offline actions
- `UserProfile` - Local user data
- `ApiKeys` - Stored credentials

## Offline Sync Flow

```
User action offline
    ↓
Add to SyncQueue (CoreData)
    ↓
App goes online
    ↓
SyncQueue detects connectivity
    ↓
Batch upload changes
    ↓
Server returns conflicts
    ↓
Resolve conflicts locally
    ↓
Mark synced
```

## Error Handling

```swift
do {
    let content = try await client.content.generate(prompt: "...")
} catch SureshError.unauthorized {
    // Refresh token or re-login
} catch SureshError.rateLimited {
    // Wait before retrying
} catch SureshError.offline {
    // Queue for later sync
}
```

## Testing

```bash
cd suresh-ios-sdk
swift test
```

Mock server available for offline testing.

## Deployment

```bash
# Version bump
swift package update

# Tag release
git tag v1.0.0
git push origin v1.0.0

# SPM will auto-detect
```

## Documentation
- Full API docs: https://docs.suresh-ai.com/ios
- Example app: https://github.com/suresh-ai-kingdom/suresh-ios-example
