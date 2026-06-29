import SwiftUI

struct TrafficLightPanelView: View {
    @EnvironmentObject private var store: ClaudeStatusStore
    @State private var isBlinking = false

    var body: some View {
        let status = store.snapshot.status

        VStack(spacing: 6) {
            ZStack {
                PixelTrafficLightPet(status: status, isBlinking: isBlinking)
            }
            .frame(width: 210, height: 126)

            StatusCaptionView(
                title: status.title,
                accentColor: status.accentColor
            )
            .offset(y: -16)
        }
        .frame(width: 210, height: 182)
        .padding(6)
        .background(Color.clear)
        .task {
            while !Task.isCancelled {
                try? await Task.sleep(for: .seconds(2.8))
                isBlinking = true
                try? await Task.sleep(for: .milliseconds(140))
                isBlinking = false
            }
        }
    }
}

private struct PixelTrafficLightPet: View {
    let status: ClaudeLightStatus
    let isBlinking: Bool

    var body: some View {
        ZStack {
            PixelTrafficLightView(status: status)
                .offset(y: -32)

            PixelClaudePetView(status: status, isBlinking: isBlinking)
                .offset(y: 16)
        }
    }
}

private struct PixelTrafficLightView: View {
    let status: ClaudeLightStatus

    private let housing = Color.black.opacity(0.88)
    private let housingInner = Color(red: 0.08, green: 0.08, blue: 0.07)

    var body: some View {
        ZStack {
            PixelArtView(
                width: 17,
                height: 5,
                pixelSize: 4,
                pixels: [
                    PixelRect(x: 0, y: 0, width: 17, height: 5, color: housing),
                    PixelRect(x: 1, y: 1, width: 15, height: 3, color: housingInner),
                    PixelRect(x: 2, y: 2, width: 4, height: 2, color: lampColor(for: .approval)),
                    PixelRect(x: 6, y: 2, width: 4, height: 2, color: lampColor(for: .working)),
                    PixelRect(x: 10, y: 2, width: 4, height: 2, color: lampColor(for: .idle))
                ]
            )
        }
    }

    private func lampColor(for state: ClaudeLightStatus) -> Color {
        if state == status {
            return state.accentColor
        }

        switch state {
        case .approval:
            return Color(red: 0.24, green: 0.08, blue: 0.09)
        case .working:
            return Color(red: 0.30, green: 0.22, blue: 0.06)
        case .idle:
            return Color(red: 0.06, green: 0.19, blue: 0.10)
        }
    }
}

private struct PixelClaudePetView: View {
    let status: ClaudeLightStatus
    let isBlinking: Bool

    private let skin = Color(red: 0.92, green: 0.58, blue: 0.47)
    private let eye = Color.black.opacity(0.92)

    @State private var floatOffset: CGFloat = 0
    @State private var armOffsetX: CGFloat = 0
    @State private var armOffsetY: CGFloat = 0
    @State private var isHovering = false

    /// Body pixels without the left arm (which animates independently)
    private var bodyPixels: [PixelRect] {
        [
            PixelRect(x: 3, y: 0, width: 12, height: 7, color: skin),
            PixelRect(x: 15, y: 4, width: 2, height: 2, color: skin),
            PixelRect(x: 6, y: isBlinking ? 3 : 2, width: 1, height: isBlinking ? 1 : 2, color: eye),
            PixelRect(x: 11, y: isBlinking ? 3 : 2, width: 1, height: isBlinking ? 1 : 2, color: eye),
            PixelRect(x: 5, y: 7, width: 1, height: 2, color: skin),
            PixelRect(x: 7, y: 7, width: 1, height: 2, color: skin),
            PixelRect(x: 10, y: 7, width: 1, height: 2, color: skin),
            PixelRect(x: 12, y: 7, width: 1, height: 2, color: skin)
        ]
    }

    /// Left arm at base position (1, 4), will animate up toward head on hover
    private var leftArmPixels: [PixelRect] {
        [
            PixelRect(x: 1, y: 4, width: 2, height: 2, color: skin)
        ]
    }

    var body: some View {
        ZStack {
            PixelArtView(
                width: 18,
                height: 10,
                pixelSize: 6,
                pixels: bodyPixels
            )

            PixelArtView(
                width: 18,
                height: 10,
                pixelSize: 6,
                pixels: leftArmPixels
            )
            .offset(x: armOffsetX, y: armOffsetY)
        }
        .offset(y: floatOffset)
        .onHover { hovering in
            isHovering = hovering
        }
        .task {
            let floatDuration: TimeInterval = 2.8
            let patCycleDuration: TimeInterval = 1.05

            while !Task.isCancelled {
                let now = Date().timeIntervalSince1970

                // Idle float
                if status == .idle {
                    let phase = now.truncatingRemainder(dividingBy: floatDuration) / floatDuration
                    floatOffset = sin(phase * .pi * 2) * 3
                } else {
                    floatOffset = 0
                }

                // Head pat: left arm lifts up to head, taps, and returns
                if isHovering {
                    let progress = now.truncatingRemainder(dividingBy: patCycleDuration) / patCycleDuration
                    if progress < 0.25 {
                        // Arm lifts up toward head
                        let t = progress / 0.25
                        armOffsetX = t * 6   // 1 pixel right (pixelSize 6)
                        armOffsetY = -t * 18  // 3 pixels up
                    } else if progress < 0.4 {
                        // Brief tap at head
                        armOffsetX = 6
                        armOffsetY = -18
                    } else if progress < 0.65 {
                        // Arm returns down
                        let t = (progress - 0.4) / 0.25
                        armOffsetX = (1 - t) * 6
                        armOffsetY = -(1 - t) * 18
                    } else {
                        // Pause at rest
                        armOffsetX = 0
                        armOffsetY = 0
                    }
                } else {
                    armOffsetX = 0
                    armOffsetY = 0
                }

                try? await Task.sleep(for: .milliseconds(16))
            }
        }
    }
}

private struct PixelArtView: View {
    let width: Int
    let height: Int
    let pixelSize: CGFloat
    let pixels: [PixelRect]

    var body: some View {
        ZStack(alignment: .topLeading) {
            ForEach(pixels) { pixel in
                Rectangle()
                    .fill(pixel.color)
                    .frame(
                        width: CGFloat(pixel.width) * pixelSize,
                        height: CGFloat(pixel.height) * pixelSize
                    )
                    .offset(
                        x: CGFloat(pixel.x) * pixelSize,
                        y: CGFloat(pixel.y) * pixelSize
                    )
            }
        }
        .frame(
            width: CGFloat(width) * pixelSize,
            height: CGFloat(height) * pixelSize,
            alignment: .topLeading
        )
        .drawingGroup(opaque: false)
    }
}

private struct StatusCaptionView: View {
    let title: String
    let accentColor: Color

    var body: some View {
        VStack(spacing: 0) {
            Text(title)
                .font(.system(size: 13, weight: .bold, design: .monospaced))
                .foregroundStyle(Color.white.opacity(0.95))
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 9)
        .background(
            Rectangle()
                .fill(Color.black.opacity(0.72))
                .overlay(
                    Rectangle()
                        .stroke(accentColor.opacity(0.5), lineWidth: 1)
                )
        )
    }
}

struct MenuBarStatusView: View {
    let status: ClaudeLightStatus

    var body: some View {
        Image(nsImage: menuBarIcon)
    }

    /// Pixel-perfect copy of PixelClaudePetView, scaled to menu bar size.
    /// Template mode adapts to light/dark system appearance automatically.
    private var menuBarIcon: NSImage {
        let q: CGFloat = 2
        let w = 18 * q   // 36pt
        let h = 10 * q   // 20pt

        let image = NSImage(size: NSSize(width: w, height: h), flipped: true) { _ in
            guard let ctx = NSGraphicsContext.current else { return false }

            NSColor.black.setFill()

            // Body
            NSBezierPath(rect: NSRect(x: 3*q, y: 0, width: 12*q, height: 7*q)).fill()
            // Left arm
            NSBezierPath(rect: NSRect(x: 1*q, y: 4*q, width: 2*q, height: 2*q)).fill()
            // Right arm
            NSBezierPath(rect: NSRect(x: 15*q, y: 4*q, width: 2*q, height: 2*q)).fill()

            // Eyes — cut transparent holes in the body
            ctx.saveGraphicsState()
            ctx.compositingOperation = .clear
            NSBezierPath(rect: NSRect(x: 6*q, y: 2*q, width: 1*q, height: 2*q)).fill()
            NSBezierPath(rect: NSRect(x: 11*q, y: 2*q, width: 1*q, height: 2*q)).fill()
            ctx.restoreGraphicsState()

            // Legs
            NSColor.black.setFill()
            NSBezierPath(rect: NSRect(x: 5*q, y: 7*q, width: 1*q, height: 2*q)).fill()
            NSBezierPath(rect: NSRect(x: 7*q, y: 7*q, width: 1*q, height: 2*q)).fill()
            NSBezierPath(rect: NSRect(x: 10*q, y: 7*q, width: 1*q, height: 2*q)).fill()
            NSBezierPath(rect: NSRect(x: 12*q, y: 7*q, width: 1*q, height: 2*q)).fill()

            return true
        }

        image.isTemplate = true
        return image
    }
}

private struct PixelRect: Identifiable {
    var id: String { "\(x),\(y),\(width),\(height)" }
    let x: Int
    let y: Int
    let width: Int
    let height: Int
    let color: Color
}
