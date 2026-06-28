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

            PixelClaudePetView(isBlinking: isBlinking)
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
    let isBlinking: Bool

    private let skin = Color(red: 0.92, green: 0.58, blue: 0.47)
    private let eye = Color.black.opacity(0.92)

    var body: some View {
        PixelArtView(
            width: 18,
            height: 10,
            pixelSize: 6,
            pixels: [
                PixelRect(x: 3, y: 0, width: 12, height: 7, color: skin),
                PixelRect(x: 1, y: 4, width: 2, height: 2, color: skin),
                PixelRect(x: 15, y: 4, width: 2, height: 2, color: skin),
                PixelRect(x: 6, y: isBlinking ? 3 : 2, width: 1, height: isBlinking ? 1 : 2, color: eye),
                PixelRect(x: 11, y: isBlinking ? 3 : 2, width: 1, height: isBlinking ? 1 : 2, color: eye),
                PixelRect(x: 5, y: 7, width: 1, height: 2, color: skin),
                PixelRect(x: 7, y: 7, width: 1, height: 2, color: skin),
                PixelRect(x: 11, y: 7, width: 1, height: 2, color: skin),
                PixelRect(x: 13, y: 7, width: 1, height: 2, color: skin)
            ]
        )
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
        HStack(spacing: 5) {
            ZStack(alignment: .top) {
                PixelArtView(
                    width: 11,
                    height: 10,
                    pixelSize: 2,
                    pixels: [
                        PixelRect(x: 1, y: 0, width: 8, height: 2, color: .black),
                        PixelRect(x: 2, y: 1, width: 2, height: 1, color: lampColor(for: .approval)),
                        PixelRect(x: 4, y: 1, width: 2, height: 1, color: lampColor(for: .working)),
                        PixelRect(x: 6, y: 1, width: 2, height: 1, color: lampColor(for: .idle)),
                        PixelRect(x: 2, y: 3, width: 7, height: 3, color: Color(red: 0.92, green: 0.58, blue: 0.47)),
                        PixelRect(x: 1, y: 4, width: 1, height: 1, color: Color(red: 0.92, green: 0.58, blue: 0.47)),
                        PixelRect(x: 9, y: 4, width: 1, height: 1, color: Color(red: 0.92, green: 0.58, blue: 0.47)),
                        PixelRect(x: 4, y: 4, width: 1, height: 1, color: .black),
                        PixelRect(x: 7, y: 4, width: 1, height: 1, color: .black),
                        PixelRect(x: 3, y: 6, width: 1, height: 2, color: Color(red: 0.92, green: 0.58, blue: 0.47)),
                        PixelRect(x: 4, y: 6, width: 1, height: 2, color: Color(red: 0.92, green: 0.58, blue: 0.47)),
                        PixelRect(x: 7, y: 6, width: 1, height: 2, color: Color(red: 0.92, green: 0.58, blue: 0.47)),
                        PixelRect(x: 8, y: 6, width: 1, height: 2, color: Color(red: 0.92, green: 0.58, blue: 0.47)),
                        PixelRect(x: 3, y: 8, width: 6, height: 1, color: .black)
                    ]
                )
            }

            Text("CC")
                .font(.system(size: 10, weight: .bold, design: .monospaced))
        }
        .padding(.horizontal, 2)
    }

    private func lampColor(for state: ClaudeLightStatus) -> Color {
        state == status ? state.accentColor : Color.black.opacity(0.45)
    }
}

private struct PixelRect: Identifiable {
    let id = UUID()
    let x: Int
    let y: Int
    let width: Int
    let height: Int
    let color: Color
}
