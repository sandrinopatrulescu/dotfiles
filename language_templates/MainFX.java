

import javafx.application.Application;
import javafx.stage.Stage;
import javafx.scene.Scene;
import javafx.scene.layout.StackPane;



import java.io.IOException;


public class MainFX extends Application {

    public static void main(String[] args) {
        launch(args);    
    }


    public void start(Stage stage) throws IOException {
        Scene scene = new Scene(new StackPane(), 500, 500);
        stage.setScene(scene);
        stage.setTitle("MainFX");
        stage.show();
    }
}
