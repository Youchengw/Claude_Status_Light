// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "ClaudeStatusLight",
    platforms: [
        .macOS(.v14)
    ],
    products: [
        .executable(
            name: "ClaudeStatusLight",
            targets: ["ClaudeStatusLight"]
        )
    ],
    targets: [
        .executableTarget(
            name: "ClaudeStatusLight",
            path: "Sources"
        )
    ]
)
