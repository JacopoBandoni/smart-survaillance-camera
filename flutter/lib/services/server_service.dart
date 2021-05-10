class ServerService {
  String serverUrl;
  String cameraUrl;
  String videoSource;

  ServerService();

  setUrl({String serverUrl, String cameraUrl, String videoSource}) {
    this.serverUrl = serverUrl;
    this.cameraUrl = cameraUrl;
    this.videoSource = videoSource;
  }
}
