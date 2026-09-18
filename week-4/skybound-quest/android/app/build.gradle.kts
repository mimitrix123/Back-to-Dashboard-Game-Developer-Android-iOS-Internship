plugins {
    id("com.android.application")
    id("com.chaquo.python")
}

android {
    namespace = "com.example.skyboundquest"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.example.skyboundquest"
        minSdk = 23
        targetSdk = 35
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }

    sourceSets["main"].assets.srcDir("src/main/python")
}

chaquopy {
    defaultConfig {
        version = "3.11"
        pip {
            install("pygame==2.5.2")
        }
    }
}
