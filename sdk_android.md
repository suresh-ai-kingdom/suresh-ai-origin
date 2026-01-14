# Android SDK (Kotlin)

## Overview
Official Kotlin library for Android integration with SURESH AI ORIGIN.

## Installation

```gradle
// build.gradle.kts
dependencies {
    implementation("com.sureshaiorigin:suresh-android:1.0.0")
    implementation("androidx.room:room-runtime:2.5.0")
    implementation("com.google.firebase:firebase-messaging:23.0.0")
}
```

## Quick Start

```kotlin
import com.sureshaiorigin.SureshAI
import com.sureshaiorigin.models.LoginRequest

// Initialize in Application class
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        SureshAI.init(this, apiEndpoint = "https://api.suresh-ai.com")
    }
}

// Authenticate
val response = SureshAI.auth.login(
    LoginRequest(email = "user@example.com", password = "password")
)

// Save token
SureshAI.preferences.saveToken(response.token)

// Generate content
val content = SureshAI.content.generate(
    prompt = "Write a marketing email",
    tone = "professional"
)

Log.d("SureshAI", content.text)
```

## Features

### Offline Database (Room)
```kotlin
// Automatic sync queue
val syncQueue = SureshAI.sync.queue()

// Add offline action
syncQueue.add(
    action = SyncAction.CREATE,
    resource = "content",
    data = mapOf("title" to "My Content")
)

// Auto-sync on connectivity change
SureshAI.sync.autoSync(enabled = true)
```

### Firebase Push Notifications
```kotlin
// Auto-register with FCM
class MyMessagingService : FirebaseMessagingService() {
    override fun onNewToken(token: String) {
        SureshAI.push.register(token)
    }

    override fun onMessageReceived(message: RemoteMessage) {
        SureshAI.push.handleNotification(message)
    }
}
```

### Analytics
```kotlin
// Track events
SureshAI.analytics.track(
    event = "content_generated",
    properties = mapOf("prompt" to "email", "tone" to "professional")
)

// Get usage stats
val stats = SureshAI.analytics.usage()
Log.d("SureshAI", "Credits: ${stats.creditsRemaining}")
```

### Caching
```kotlin
// Automatic Room caching
val prompts = SureshAI.content.prompts(
    cache = true,
    ttlMinutes = 60
)
```

## Architecture

### Core Components
- `SureshAI` - Singleton manager
- `AuthManager` - JWT + token refresh
- `ContentManager` - AI generation
- `SyncManager` - Room database + conflict resolution
- `PushManager` - FCM integration
- `AnalyticsManager` - Event tracking
- `CacheManager` - Room persistence

### Room Database
- `CachedContent` - Generated content
- `SyncQueueEntity` - Offline actions
- `UserProfile` - Local user data
- `ApiKey` - Stored credentials

## Offline Sync Flow

```
User action offline
    ↓
Insert to Room SyncQueueEntity
    ↓
WorkManager queues sync task
    ↓
Connectivity detected
    ↓
WorkManager runs sync
    ↓
Batch upload changes
    ↓
Process server responses
    ↓
Update local Room database
```

## Error Handling

```kotlin
try {
    val content = SureshAI.content.generate("...")
} catch (e: SureshException) {
    when (e) {
        is UnauthorizedException -> refreshToken()
        is RateLimitedException -> showRetryDialog()
        is OfflineException -> queueForSync()
    }
}
```

## WorkManager Integration

```kotlin
// Background sync task
class SureshSyncWorker : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        return try {
            SureshAI.sync.syncQueue()
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}

// Schedule
PeriodicWorkRequestBuilder<SureshSyncWorker>(
    Duration.ofHours(1)
).build().let {
    WorkManager.getInstance(context).enqueueUniquePeriodicWork(
        "suresh_sync",
        ExistingPeriodicWorkPolicy.KEEP,
        it
    )
}
```

## Testing

```bash
cd suresh-android-sdk
./gradlew test
./gradlew connectedAndroidTest  # Instrumented tests
```

Mock server + Room in-memory database for testing.

## Proguard Rules

```proguard
# suresh-rules.pro
-keep class com.sureshaiorigin.** { *; }
-keepclassmembers class com.sureshaiorigin.** { *; }
```

## Documentation
- Full API docs: https://docs.suresh-ai.com/android
- Example app: https://github.com/suresh-ai-kingdom/suresh-android-example
- Kotlin docs: https://kotlinlang.org/docs/home.html
