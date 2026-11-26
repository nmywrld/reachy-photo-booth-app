/**
 * SPDX-License-Identifier: Apache-2.0
 */

import classNames from "classnames";
import type { MirrorPhoto } from "./types/api";
import QRCode from "./QRCode";

interface MirrorPhotoCardProps {
  className?: string;
  photo: MirrorPhoto;
}

const STATUS_TEXT: Record<MirrorPhoto["status"], string> = {
  processing: "Painting the hi-res version… it will appear on your phone too",
  ready: "Hi-res version ready! Scan to download",
  failed: "Scan to download your photo"
};

/** The shutter result: the photo (instant, then hi-res) with its QR code. */
export default function MirrorPhotoCard({ className, photo }: MirrorPhotoCardProps) {
  const image = photo.hires_image ?? photo.instant_image;
  return (
    <div
      className={classNames(
        "flex flex-col items-center gap-[2vh] rounded-3xl bg-black/70 p-[2.5vh] shadow-2xl backdrop-blur-md",
        className
      )}
    >
      <img
        key={image}
        src={image}
        alt="Your photo"
        className="max-h-[52vh] w-full rounded-2xl object-contain"
      />
      <div className="flex w-full flex-row items-center gap-[2vh]">
        {photo.qr_code && <QRCode className="w-[14vh] shrink-0" url={photo.qr_code} />}
        <p className="text-[2.6vh] leading-tight">
          {STATUS_TEXT[photo.status]}
          {photo.status === "processing" && (
            <span className="ml-2 inline-block animate-pulse">●</span>
          )}
        </p>
      </div>
    </div>
  );
}
