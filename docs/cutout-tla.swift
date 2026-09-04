import Foundation
import Vision
import CoreImage
import AppKit

// Wycięcie pierwszego planu (osoby) ze zdjęcia — Vision, lokalnie, bez sieci.
// użycie: swift cutout.swift wejscie.jpg wyjscie.png [numer-instancji]
//
// Bez numeru instancji wycina cały pierwszy plan. Zdjęcia z dwiema osobami
// (pielęgniarka i pacjentka) mają dwie instancje — wtedy podaj numer, np. 1,
// żeby dostać samą pielęgniarkę, przyciętą do jej obrysu.

let args = CommandLine.arguments
guard args.count >= 3 else { FileHandle.standardError.write("usage: cutout <in> <out> [instancja]\n".data(using:.utf8)!); exit(2) }
let inURL = URL(fileURLWithPath: args[1])
let outURL = URL(fileURLWithPath: args[2])
let wanted = args.count > 3 ? Int(args[3]) : nil

let handler = VNImageRequestHandler(url: inURL, options: [:])
let request = VNGenerateForegroundInstanceMaskRequest()

do {
    try handler.perform([request])
    guard let result = request.results?.first else {
        FileHandle.standardError.write("brak wykrytego pierwszego planu\n".data(using:.utf8)!)
        exit(1)
    }
    var instances = result.allInstances
    if let n = wanted {
        let all = Array(result.allInstances).sorted()
        guard n >= 1, n <= all.count else {
            FileHandle.standardError.write("jest \(all.count) instancji, poproszono o \(n)\n".data(using:.utf8)!)
            exit(1)
        }
        instances = IndexSet(integer: all[n - 1])
    }
    let buffer = try result.generateMaskedImage(ofInstances: instances,
                                                from: handler,
                                                croppedToInstancesExtent: wanted != nil)
    let ci = CIImage(cvPixelBuffer: buffer)
    let ctx = CIContext()
    guard let png = ctx.pngRepresentation(of: ci,
                                          format: .RGBA8,
                                          colorSpace: CGColorSpace(name: CGColorSpace.sRGB)!) else {
        FileHandle.standardError.write("nie udało się zakodować PNG\n".data(using:.utf8)!)
        exit(1)
    }
    try png.write(to: outURL)
    print("ok \(Int(ci.extent.width))x\(Int(ci.extent.height)) instancji=\(result.allInstances.count)")
} catch {
    FileHandle.standardError.write("błąd: \(error)\n".data(using:.utf8)!)
    exit(1)
}
