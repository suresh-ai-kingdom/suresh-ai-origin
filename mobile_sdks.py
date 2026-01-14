"""Mobile SDK - Web (TypeScript/JavaScript) with offline support."""
import json
import uuid
import time
from typing import Dict, List

class WebSDK:
    """Web SDK for JavaScript/TypeScript applications."""
    
    LATEST_VERSION = "2.0.0"
    
    @staticmethod
    def get_sdk_package() -> Dict:
        """Get SDK npm package info."""
        return {
            "name": "@suresh-ai/sdk",
            "version": WebSDK.LATEST_VERSION,
            "description": "Official Web SDK for SURESH AI ORIGIN",
            "main": "dist/index.js",
            "types": "dist/index.d.ts",
            "repository": "github.com/suresh-ai-kingdom/suresh-ai-sdk",
            "keywords": ["ai", "content-generation", "offline-sync"],
            "dependencies": {
                "axios": "^1.4.0",
                "dexie": "^3.2.4",  # IndexedDB wrapper
                "jwt-decode": "^3.1.2",
            },
            "devDependencies": {
                "typescript": "^5.0.0",
                "jest": "^29.0.0",
                "@types/node": "^20.0.0",
            }
        }
    
    @staticmethod
    def get_installation_guide() -> str:
        """Get SDK installation guide."""
        return """
# SURESH AI ORIGIN - Web SDK

## Installation

```bash
npm install @suresh-ai/sdk
# or
yarn add @suresh-ai/sdk
```

## Quick Start

```typescript
import { SureshAIClient } from '@suresh-ai/sdk';

const client = new SureshAIClient({
  baseURL: 'https://api.suresh-ai.com',
  apiVersion: 'v2',
});

// Login
const { token } = await client.auth.login('user@example.com', 'password');

// Generate content
const content = await client.content.generate({
  prompt: 'Write a blog post about AI',
  templateId: 'blog_post',
});

// Offline sync
await client.sync.push();  // Push offline changes
const changes = await client.sync.pull();  // Pull remote changes
```

## Offline Support

The SDK automatically:
- Caches responses in IndexedDB
- Queues requests when offline
- Syncs when connection restored
- Handles conflict resolution

## Features

- ✅ JWT Authentication (7-day tokens)
- ✅ Offline-first with sync
- ✅ IndexedDB caching
- ✅ Automatic retry logic
- ✅ TypeScript support
- ✅ ESM & CommonJS bundles
"""
    
    @staticmethod
    def get_typescript_examples() -> Dict:
        """Get TypeScript code examples."""
        return {
            "initialization": """
import { SureshAIClient, OfflineSyncQueue } from '@suresh-ai/sdk';

const client = new SureshAIClient({
  baseURL: process.env.REACT_APP_API_URL,
  apiVersion: 'v2',
  tier: 'pro',
});

// Enable offline sync
const syncQueue = new OfflineSyncQueue();
client.enableOfflineSync(syncQueue);
""",
            "authentication": """
// Login
const response = await client.auth.login({
  email: 'user@example.com',
  password: 'password'
});
console.log('Token:', response.token);
console.log('User:', response.user);

// Refresh token
const newToken = await client.auth.refresh(token);

// Logout
await client.auth.logout();
""",
            "content_generation": """
// Generate content
const content = await client.content.generate({
  prompt: 'Write a product description',
  templateId: 'product_description',
  context: { product: 'iPhone 15' }
});

// List prompts
const prompts = await client.content.listPrompts();

// Get content by ID
const saved = await client.content.get(contentId);
""",
            "offline_sync": """
// Offline sync automatically queues requests

// Push offline changes
const pushed = await client.sync.push();
console.log('Pushed:', pushed.count, 'items');

// Pull remote changes
const pulled = await client.sync.pull();
console.log('Pulled:', pulled.count, 'items');

// Check sync status
const status = await client.sync.status();
console.log('Pending:', status.pending.length);
console.log('Synced:', status.synced.length);
""",
            "error_handling": """
try {
  const content = await client.content.generate({...});
} catch (error) {
  if (error.code === 'UNAUTHORIZED') {
    // Token expired, refresh or re-login
    await client.auth.refresh(token);
  } else if (error.code === 'RATE_LIMITED') {
    // Wait before retrying
    console.log('Rate limited, retry after:', error.retryAfter);
  }
}
""",
        }


class iOSSDK:
    """iOS SDK for Swift applications."""
    
    LATEST_VERSION = "2.0.0"
    
    @staticmethod
    def get_installation_guide() -> str:
        """Get iOS SDK installation guide."""
        return """
# SURESH AI ORIGIN - iOS SDK

## Installation

### CocoaPods

Add to your Podfile:
```ruby
pod 'SureshAISDK', '~> 2.0'
```

Then run:
```bash
pod install
```

### SPM (Swift Package Manager)

In Xcode:
1. File → Add Packages
2. Enter: https://github.com/suresh-ai-kingdom/suresh-ai-ios-sdk.git
3. Select version 2.0.0+

## Quick Start

```swift
import SureshAISDK

let client = SureshAIClient(
    baseURL: "https://api.suresh-ai.com",
    apiVersion: "v2"
)

// Login
do {
    let response = try await client.auth.login(
        email: "user@example.com",
        password: "password"
    )
    print("Token: \\(response.token)")
} catch {
    print("Login failed: \\(error)")
}

// Generate content
let content = try await client.content.generate(
    prompt: "Write a blog post",
    templateId: "blog_post"
)
```

## Offline Support

- CoreData for local persistence
- Automatic sync when online
- Conflict resolution
- Queue management

## Features

- ✅ Swift async/await
- ✅ CoreData offline storage
- ✅ Push notifications
- ✅ Background sync
- ✅ Full type safety
"""
    
    @staticmethod
    def get_swift_examples() -> Dict:
        """Get Swift code examples."""
        return {
            "setup": """
import SureshAISDK

let client = SureshAIClient(
    baseURL: "https://api.suresh-ai.com",
    apiVersion: "v2"
)

// Configure push notifications
client.setPushNotificationDelegate(NotificationDelegate())
""",
            "authentication": """
// Login
async {
    do {
        let response = try await client.auth.login(
            email: "user@example.com",
            password: "password"
        )
        UserDefaults.standard.set(response.token, forKey: "auth_token")
    } catch {
        print("Login error: \\(error)")
    }
}

// Refresh token
let newToken = try await client.auth.refresh(currentToken)

// Logout
try await client.auth.logout()
""",
            "offline_storage": """
// CoreData is automatically synced
let content = Content(
    id: UUID(),
    title: "My Content",
    body: "Content text",
    status: .pending
)

try await client.storage.save(content)

// Sync when online
client.enableAutoSync()  // Syncs every 5 minutes when online
""",
        }


class AndroidSDK:
    """Android SDK for Kotlin applications."""
    
    LATEST_VERSION = "2.0.0"
    
    @staticmethod
    def get_installation_guide() -> str:
        """Get Android SDK installation guide."""
        return """
# SURESH AI ORIGIN - Android SDK

## Installation

Add to your build.gradle:

```gradle
dependencies {
    implementation 'com.suresh-ai:sdk:2.0.0'
    implementation 'androidx.room:room-runtime:2.5.1'
}
```

## Quick Start

```kotlin
import com.sureshaiorigin.sdk.SureshAIClient

val client = SureshAIClient.Builder()
    .baseURL("https://api.suresh-ai.com")
    .apiVersion("v2")
    .build()

// Login
lifecycleScope.launch {
    try {
        val response = client.auth.login("user@example.com", "password")
        println("Token: ${response.token}")
    } catch (e: Exception) {
        println("Login failed: ${e.message}")
    }
}

// Generate content
val content = client.content.generate(
    prompt = "Write a blog post",
    templateId = "blog_post"
)
```

## Offline Support

- Room Database for persistence
- WorkManager for background sync
- Automatic conflict resolution
- Queue-based syncing

## Features

- ✅ Kotlin coroutines
- ✅ Room Database
- ✅ WorkManager background sync
- ✅ Push notifications
- ✅ Full type safety
"""
    
    @staticmethod
    def get_kotlin_examples() -> Dict:
        """Get Kotlin code examples."""
        return {
            "setup": """
import com.sureshaiorigin.sdk.SureshAIClient

val client = SureshAIClient.Builder()
    .baseURL("https://api.suresh-ai.com")
    .apiVersion("v2")
    .tier(UserTier.PRO)
    .build()

// Enable background sync
client.enableAutoSync(intervalMinutes = 5)
""",
            "authentication": """
lifecycleScope.launch {
    try {
        val response = client.auth.login(
            email = "user@example.com",
            password = "password"
        )
        val token = response.token
        val user = response.user
    } catch (e: AuthException) {
        Log.e("Auth", "Login failed", e)
    }
}
""",
            "offline_database": """
// Room Database automatically syncs
val content = Content(
    id = UUID.randomUUID().toString(),
    title = "My Content",
    body = "Content text",
    status = SyncStatus.PENDING
)

client.storage.save(content)

// WorkManager handles background sync
client.sync.pushAsync()  // Queue and sync when online
""",
        }
