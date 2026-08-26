interface Props {
  annotatedUrl: string;
}

export function VideoPlayer({ annotatedUrl }: Props) {
  return (
    <video controls className="w-full rounded-lg border border-gray-200 dark:border-gray-800">
      <source src={annotatedUrl} />
      您的浏览器不支持视频播放。
    </video>
  );
}
