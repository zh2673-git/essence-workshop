import React from 'react';
import { staticFile } from './static-file.js';

export interface ImgProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  src: string;
}

export const Img: React.FC<ImgProps> = ({ src, ...props }) => {
  return <img src={staticFile(src)} {...props} />;
};

export interface VideoProps extends React.VideoHTMLAttributes<HTMLVideoElement> {
  src: string;
}

export const Video: React.FC<VideoProps> = ({ src, ...props }) => {
  return <video src={staticFile(src)} {...props} />;
};

export interface AudioProps extends React.AudioHTMLAttributes<HTMLAudioElement> {
  src: string;
}

export const Audio: React.FC<AudioProps> = ({ src, ...props }) => {
  return <audio src={staticFile(src)} {...props} />;
};
