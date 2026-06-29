import Foundation
import SwiftUI

enum ClaudeLightStatus: String, Codable, CaseIterable {
    case idle
    case working
    case approval

    var title: String {
        switch self {
        case .idle:
            return "Idle"
        case .working:
            return "Working"
        case .approval:
            return "Awaiting you"
        }
    }

    var menuDescription: String {
        switch self {
        case .idle:
            return "Claude is idle."
        case .working:
            return "Claude is working."
        case .approval:
            return "Claude is waiting for you."
        }
    }

    var accentColor: Color {
        switch self {
        case .idle:
            return Color(red: 0.38, green: 0.97, blue: 0.58)
        case .working:
            return Color(red: 1.00, green: 0.78, blue: 0.23)
        case .approval:
            return Color(red: 1.00, green: 0.35, blue: 0.42)
        }
    }

    var activeLamp: TrafficLamp {
        switch self {
        case .idle:
            return .green
        case .working:
            return .yellow
        case .approval:
            return .red
        }
    }
}

enum TrafficLamp: CaseIterable, Hashable {
    case red
    case yellow
    case green

    var offColor: Color {
        switch self {
        case .red:
            return Color(red: 0.32, green: 0.08, blue: 0.11)
        case .yellow:
            return Color(red: 0.34, green: 0.22, blue: 0.04)
        case .green:
            return Color(red: 0.05, green: 0.24, blue: 0.12)
        }
    }

    var onColor: Color {
        switch self {
        case .red:
            return Color(red: 1.00, green: 0.35, blue: 0.42)
        case .yellow:
            return Color(red: 1.00, green: 0.78, blue: 0.23)
        case .green:
            return Color(red: 0.38, green: 0.97, blue: 0.58)
        }
    }
}

struct ClaudeStatusSnapshot: Codable, Equatable {
    var status: ClaudeLightStatus
    var updatedAt: Date
    var source: String
    var detail: String?
    var sessionId: String?
    var hookEventName: String?
    var toolName: String?
    var cwd: String?

    static let placeholder = ClaudeStatusSnapshot(
        status: .idle,
        updatedAt: .now,
        source: "startup",
        detail: "Waiting for Claude Code"
    )
}

enum ClaudeStatusFile {
    static var url: URL {
        if let override = ProcessInfo.processInfo.environment["CLAUDE_STATUS_LIGHT_FILE"], !override.isEmpty {
            return URL(fileURLWithPath: override)
        }

        let appSupport = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first!
        return appSupport
            .appendingPathComponent("ClaudeStatusLight", isDirectory: true)
            .appendingPathComponent("status.json", isDirectory: false)
    }

    static func write(status: ClaudeLightStatus, source: String, detail: String? = nil) throws {
        let fileURL = url
        try FileManager.default.createDirectory(
            at: fileURL.deletingLastPathComponent(),
            withIntermediateDirectories: true,
            attributes: nil
        )

        let snapshot = ClaudeStatusSnapshot(
            status: status,
            updatedAt: .now,
            source: source,
            detail: detail
        )

        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        encoder.dateEncodingStrategy = .iso8601

        let data = try encoder.encode(snapshot)
        try data.write(to: fileURL, options: .atomic)
    }
}

@MainActor
final class ClaudeStatusStore: ObservableObject {
    @Published private(set) var snapshot = ClaudeStatusSnapshot.placeholder

    private var source: DispatchSourceFileSystemObject?
    private var monitoredFD: Int32 = -1

    init() {
        loadSnapshot()
        startMonitoring()
    }

    deinit {
        source?.cancel()
    }

    private func startMonitoring() {
        // Tear down any existing source before opening a new fd so the
        // cancel handler closes the right descriptor.
        if let oldSource = source {
            oldSource.cancel()
            source = nil
        }

        let fileURL = ClaudeStatusFile.url
        let dirURL = fileURL.deletingLastPathComponent()

        // Ensure the directory exists before we try to open a file inside it.
        try? FileManager.default.createDirectory(
            at: dirURL, withIntermediateDirectories: true
        )

        let fd = open(fileURL.path, O_EVTONLY | O_CREAT, 0o644)
        guard fd >= 0 else { return }

        monitoredFD = fd
        let src = DispatchSource.makeFileSystemObjectSource(
            fileDescriptor: fd,
            eventMask: [.write, .extend, .delete],
            queue: .main
        )

        src.setEventHandler { [weak self] in
            let events = src.data
            if events.contains(.delete) {
                // Atomic write (write-then-rename) deletes the old inode —
                // re-open to monitor the new inode.
                self?.startMonitoring()
            } else {
                self?.loadSnapshot()
            }
        }

        src.setCancelHandler {
            // Capture fd by value so we close the inode this source was watching.
            close(fd)
        }

        src.resume()
        source = src
    }

    private func loadSnapshot() {
        let fileURL = ClaudeStatusFile.url
        guard let data = try? Data(contentsOf: fileURL) else {
            if snapshot.source != "startup" {
                snapshot = .placeholder
            }
            return
        }

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        decoder.keyDecodingStrategy = .convertFromSnakeCase

        guard let decoded = try? decoder.decode(ClaudeStatusSnapshot.self, from: data) else {
            return
        }

        if decoded != snapshot {
            snapshot = decoded
        }
    }
}
