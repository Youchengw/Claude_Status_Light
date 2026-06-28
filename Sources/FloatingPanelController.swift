import AppKit
import SwiftUI

final class FloatingWindow: NSWindow {
    override var canBecomeKey: Bool { true }
    override var canBecomeMain: Bool { true }
}

final class FloatingPanelController: NSWindowController, NSWindowDelegate {
    private let onMove: (NSPoint) -> Void
    static let defaultSize = NSSize(width: 222, height: 194)

    init<Content: View>(rootView: Content, onMove: @escaping (NSPoint) -> Void = { _ in }) {
        self.onMove = onMove
        let hostingController = NSHostingController(rootView: rootView)

        let panel = FloatingWindow(
            contentRect: NSRect(origin: .zero, size: Self.defaultSize),
            styleMask: [.borderless],
            backing: .buffered,
            defer: false
        )

        panel.level = .floating
        panel.collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary]
        panel.isOpaque = false
        panel.backgroundColor = .clear
        panel.hasShadow = false
        panel.isReleasedWhenClosed = false
        panel.isMovableByWindowBackground = true
        panel.isExcludedFromWindowsMenu = true
        panel.contentViewController = hostingController
        panel.setContentSize(Self.defaultSize)
        panel.delegate = nil

        super.init(window: panel)
        shouldCascadeWindows = false
        panel.delegate = self
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    func windowDidMove(_ notification: Notification) {
        guard let origin = window?.frame.origin else {
            return
        }

        onMove(origin)
    }
}
