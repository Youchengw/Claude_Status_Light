import AppKit
import SwiftUI

final class AppDelegate: NSObject, NSApplicationDelegate {
    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.accessory)
    }
}

@main
struct ClaudeStatusLightApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) private var appDelegate
    @StateObject private var coordinator = AppCoordinator()

    var body: some Scene {
        MenuBarExtra {
            MenuContentView()
                .environmentObject(coordinator)
        } label: {
            MenuBarStatusView(status: coordinator.store.snapshot.status)
        }
        .menuBarExtraStyle(.window)
    }
}
