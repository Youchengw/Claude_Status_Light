import AppKit
import ServiceManagement
import SwiftUI

@MainActor
final class AppCoordinator: ObservableObject {
    let store = ClaudeStatusStore()

    @Published private(set) var isPanelVisible = false
    @Published private(set) var launchAtLoginEnabled = false

    private var panelController: FloatingPanelController?
    private var hasPositionedPanel = false
    private var launchObserver: NSObjectProtocol?
    private let userDefaults = UserDefaults.standard

    private enum DefaultsKey {
        static let panelOriginX = "panel.origin.x"
        static let panelOriginY = "panel.origin.y"
    }

    init() {
        refreshLaunchAtLoginState()
        launchObserver = NotificationCenter.default.addObserver(
            forName: NSApplication.didFinishLaunchingNotification,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            Task { @MainActor [weak self] in
                self?.start()
            }
        }
    }

    func start() {
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) {
            self.showPanel(activateApp: false)
        }
    }

    deinit {
        if let launchObserver {
            NotificationCenter.default.removeObserver(launchObserver)
        }
    }

    func togglePanel() {
        if isPanelVisible {
            hidePanel()
        } else {
            showPanel()
        }
    }

    func showPanel(resetPosition: Bool = false, activateApp: Bool = true) {
        if panelController == nil {
            let rootView = TrafficLightPanelView()
                .environmentObject(store)
            panelController = FloatingPanelController(rootView: rootView) { [weak self] origin in
                self?.savePanelOrigin(origin)
            }
        }

        guard let panel = panelController?.window else {
            return
        }

        if resetPosition || !hasPositionedPanel {
            position(panel: panel, useSavedOrigin: !resetPosition)
            hasPositionedPanel = true
        }

        panelController?.showWindow(nil)
        panel.makeKeyAndOrderFront(nil)

        if activateApp {
            NSApplication.shared.activate(ignoringOtherApps: true)
        }

        panel.orderFrontRegardless()
        isPanelVisible = true
    }

    func hidePanel() {
        panelController?.window?.orderOut(nil)
        isPanelVisible = false
    }

    func resetPanelPosition() {
        showPanel(resetPosition: true)
    }

    func setLaunchAtLogin(_ enabled: Bool) {
        do {
            if enabled {
                try SMAppService.mainApp.register()
            } else {
                try SMAppService.mainApp.unregister()
            }
        } catch {
            NSSound.beep()
        }

        refreshLaunchAtLoginState()
    }

    func writePreviewStatus(_ status: ClaudeLightStatus) {
        do {
            try ClaudeStatusFile.write(status: status, source: "menu-preview", detail: "Preview from menu")
        } catch {
            NSSound.beep()
        }
    }

    func quit() {
        NSApplication.shared.terminate(nil)
    }

    private func position(panel: NSWindow, useSavedOrigin: Bool) {
        let panelSize = panel.frame.size == .zero ? FloatingPanelController.defaultSize : panel.frame.size

        if useSavedOrigin, let savedOrigin = savedPanelOrigin(for: panelSize) {
            panel.setFrameOrigin(savedOrigin)
            savePanelOrigin(savedOrigin)
            return
        }

        guard let screen = NSScreen.main ?? NSScreen.screens.first else {
            return
        }

        let visibleFrame = screen.visibleFrame
        let size = panelSize
        let x = visibleFrame.maxX - size.width - 28
        let y = visibleFrame.midY - (size.height / 2)

        let origin = NSPoint(x: x, y: y)
        panel.setFrameOrigin(origin)
        savePanelOrigin(origin)
    }

    private func savePanelOrigin(_ origin: NSPoint) {
        userDefaults.set(origin.x, forKey: DefaultsKey.panelOriginX)
        userDefaults.set(origin.y, forKey: DefaultsKey.panelOriginY)
    }

    private func savedPanelOrigin(for size: NSSize) -> NSPoint? {
        guard userDefaults.object(forKey: DefaultsKey.panelOriginX) != nil,
              userDefaults.object(forKey: DefaultsKey.panelOriginY) != nil else {
            return nil
        }

        let origin = NSPoint(
            x: userDefaults.double(forKey: DefaultsKey.panelOriginX),
            y: userDefaults.double(forKey: DefaultsKey.panelOriginY)
        )
        let panelRect = NSRect(origin: origin, size: size)
        let isVisibleOnCurrentDisplays = NSScreen.screens.contains { screen in
            screen.visibleFrame.intersects(panelRect)
        }

        return isVisibleOnCurrentDisplays ? origin : nil
    }

    private func refreshLaunchAtLoginState() {
        launchAtLoginEnabled = SMAppService.mainApp.status == .enabled
    }
}

struct MenuContentView: View {
    @EnvironmentObject private var coordinator: AppCoordinator

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Claude Status Light")
                .font(.headline)
            Text(coordinator.store.snapshot.status.menuDescription)
                .font(.subheadline)
                .foregroundStyle(.secondary)

            Divider()

            Button(coordinator.isPanelVisible ? "Hide Floating Light" : "Show Floating Light") {
                coordinator.togglePanel()
            }

            Button("Reset Floating Light Position") {
                coordinator.resetPanelPosition()
            }

            Toggle(
                "Launch at Login",
                isOn: Binding(
                    get: { coordinator.launchAtLoginEnabled },
                    set: { coordinator.setLaunchAtLogin($0) }
                )
            )

            Menu("Preview Status") {
                Button("Idle / 休息中") {
                    coordinator.writePreviewStatus(.idle)
                }
                Button("Working / 工作中") {
                    coordinator.writePreviewStatus(.working)
                }
                Button("Approval / 等你回应") {
                    coordinator.writePreviewStatus(.approval)
                }
            }

            Divider()

            Button("Quit") {
                coordinator.quit()
            }
            .keyboardShortcut("q")
        }
        .padding(14)
        .frame(width: 220)
    }
}
